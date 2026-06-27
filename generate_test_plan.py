import sys
sys.path.insert(0, r"c:\AI\3x\Chatpter_3_BLAST_FramWork\Lib\site-packages")

import os
import requests
from dotenv import load_dotenv
from groq import Groq

load_dotenv(dotenv_path=r"c:\AI\3x\Chatpter_3_BLAST_FramWork\.env")

GROQ_KEY = os.getenv("GROQ_KEY")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_URL = os.getenv("JIRA_URL")
ISSUE_KEY = "KAN-1"


def fetch_jira_issue(issue_key: str) -> dict:
    url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}"
    response = requests.get(
        url,
        auth=(JIRA_EMAIL, JIRA_API_TOKEN),
        headers={"Accept": "application/json"},
    )
    response.raise_for_status()
    return response.json()


def extract_text(adf_node) -> str:
    """Recursively extract plain text from Atlassian Document Format."""
    if not adf_node:
        return ""
    if isinstance(adf_node, str):
        return adf_node
    node_type = adf_node.get("type", "")
    text = adf_node.get("text", "")
    result = text
    for child in adf_node.get("content", []):
        result += extract_text(child)
    if node_type in ("paragraph", "heading", "listItem", "bulletList", "orderedList"):
        result += "\n"
    return result


def generate_test_plan(issue: dict) -> str:
    fields = issue.get("fields", {})
    summary = fields.get("summary", "")
    description_raw = fields.get("description", {})
    description = extract_text(description_raw).strip() if description_raw else "No description provided."
    issue_type = (fields.get("issuetype") or {}).get("name", "Unknown")
    priority = (fields.get("priority") or {}).get("name", "Unknown")
    status = (fields.get("status") or {}).get("name", "Unknown")
    assignee = (fields.get("assignee") or {}).get("displayName", "Unassigned")

    prompt = f"""You are a senior QA engineer. Given the following Jira issue, generate a comprehensive Test Plan.

---
Issue Key: {issue["key"]}
Type: {issue_type}
Priority: {priority}
Status: {status}
Assignee: {assignee}

Summary: {summary}

Description:
{description}
---

Generate a Test Plan that includes:
1. **Objective** — What is being tested and why
2. **Scope** — Features/areas in scope and out of scope
3. **Test Strategy** — Approach (unit, integration, E2E, etc.)
4. **Test Cases** — At least 5 specific, actionable test cases with:
   - Test Case ID
   - Title
   - Preconditions
   - Steps
   - Expected Result
5. **Entry & Exit Criteria**
6. **Risks & Mitigations**

Be specific and technical."""

    client = Groq(api_key=GROQ_KEY)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return response.choices[0].message.content


def main():
    print(f"Fetching Jira issue {ISSUE_KEY} from {JIRA_URL}...")
    issue = fetch_jira_issue(ISSUE_KEY)
    summary = issue.get("fields", {}).get("summary", "")
    print(f"Issue fetched: [{ISSUE_KEY}] {summary}\n")

    print("Generating Test Plan with Groq LLM...\n")
    test_plan = generate_test_plan(issue)

    output_path = r"c:\AI\3x\Chatpter_3_BLAST_FramWork\test_plan_output.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# Test Plan: {ISSUE_KEY} — {summary}\n\n")
        f.write(test_plan)

    print("=" * 60)
    print(test_plan)
    print("=" * 60)
    print(f"\nTest plan saved to: {output_path}")


if __name__ == "__main__":
    main()
