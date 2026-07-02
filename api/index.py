"""
Vercel entry point — fully self-contained Flask app.
Does not import from tools/ to avoid path resolution issues on Vercel.
"""
import os
import requests
import markdown as md_lib
from dotenv import load_dotenv
from flask import Flask, render_template, request
from groq import Groq

load_dotenv()

GROQ_KEY       = os.getenv("GROQ_KEY")
JIRA_EMAIL     = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_URL       = os.getenv("JIRA_URL")

# Templates are at /var/task/templates/ on Vercel
_HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app = Flask(__name__, template_folder=os.path.join(_HERE, "templates"))


def _extract_text(node) -> str:
    if not node:
        return ""
    if isinstance(node, str):
        return node
    text = node.get("text", "")
    for child in node.get("content", []):
        text += _extract_text(child)
    if node.get("type") in ("paragraph", "heading", "listItem", "bulletList", "orderedList"):
        text += "\n"
    return text


def _fetch_issue(issue_key: str) -> dict:
    url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}"
    resp = requests.get(
        url,
        auth=(JIRA_EMAIL, JIRA_API_TOKEN),
        headers={"Accept": "application/json"},
        timeout=10,
    )
    resp.raise_for_status()
    raw = resp.json()
    fields = raw.get("fields", {})
    return {
        "key":         raw["key"],
        "summary":     fields.get("summary", ""),
        "description": _extract_text(fields.get("description") or {}).strip() or "No description provided.",
        "issue_type":  (fields.get("issuetype") or {}).get("name", "Unknown"),
        "priority":    (fields.get("priority")  or {}).get("name", "Unknown"),
        "status":      (fields.get("status")    or {}).get("name", "Unknown"),
        "assignee":    (fields.get("assignee")  or {}).get("displayName", "Unassigned"),
    }


def _generate_test_plan(issue: dict) -> str:
    prompt = f"""You are a senior QA engineer. Given the following Jira issue, generate a comprehensive Test Plan.

---
Issue Key : {issue['key']}
Type      : {issue['issue_type']}
Priority  : {issue['priority']}
Status    : {issue['status']}
Assignee  : {issue['assignee']}
Summary   : {issue['summary']}

Description:
{issue['description']}
---

Generate a formal Test Plan that includes:
1. **Objective** - What is being tested and why
2. **Scope** - Features in scope and out of scope
3. **Test Strategy** - Approach (unit, integration, E2E, etc.)
4. **Test Cases** - Minimum 5, each with:
   - Test Case ID ({issue['key']}-TC-001, etc.)
   - Title
   - Preconditions
   - Steps (numbered)
   - Expected Result
5. **Entry & Exit Criteria**
6. **Risks & Mitigations**

Use formal, professional tone. Format test cases using Steps + Expected Result (not Gherkin)."""

    client = Groq(api_key=GROQ_KEY)
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return resp.choices[0].message.content


@app.route("/", methods=["GET", "POST"])
def index():
    test_plan_html = None
    issue_key      = ""
    summary        = ""
    error          = None

    if request.method == "POST":
        issue_key = request.form.get("issue_key", "").strip().upper()
        if not issue_key:
            error = "Please enter a Jira issue ID."
        else:
            try:
                issue          = _fetch_issue(issue_key)
                summary        = issue["summary"]
                plan_markdown  = _generate_test_plan(issue)
                test_plan_html = md_lib.markdown(plan_markdown, extensions=["tables"])
            except requests.HTTPError as e:
                code = e.response.status_code if e.response is not None else "?"
                if code in (401, 403):
                    error = f"Access denied for issue '{issue_key}'. Check Jira credentials."
                elif code == 404:
                    error = f"Issue '{issue_key}' not found in Jira."
                else:
                    error = f"Jira error {code} for issue '{issue_key}'."
            except Exception as e:
                error = f"Unexpected error: {e}"

    return render_template(
        "index.html",
        test_plan_html=test_plan_html,
        issue_key=issue_key,
        summary=summary,
        error=error,
    )


handler = app
