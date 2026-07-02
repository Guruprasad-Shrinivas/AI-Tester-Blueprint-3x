"""
Layer 2: Navigation (Flask routing layer).
Routes user input through the tool chain. Contains no business logic.
SOP: architecture/flask_app_sop.md
"""
import os
import sys
import requests
import markdown as md_lib
from dotenv import load_dotenv
from flask import Flask, render_template, request

_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _ROOT)

from tools.jira_tool import fetch_issue
from tools.llm_tool  import generate_test_plan

load_dotenv(dotenv_path=os.path.join(_ROOT, ".env"), override=True)

GROQ_KEY       = os.getenv("GROQ_KEY")
JIRA_EMAIL     = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_URL       = os.getenv("JIRA_URL")

app = Flask(__name__, template_folder=os.path.join(_ROOT, "templates"))


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
                issue         = fetch_issue(issue_key, JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN)
                summary       = issue["summary"]
                plan_markdown = generate_test_plan(issue, GROQ_KEY)
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


if __name__ == "__main__":
    print("Starting Jira Test Plan Generator on http://localhost:5000")
    app.run(debug=True, port=5000)
