"""
Layer 3 Tool: Groq LLM Test Plan Generator
Atomic, testable. No Flask imports. No Jira calls.
SOP: architecture/test_plan_generation_sop.md
"""
from groq import Groq

MODEL = "llama-3.3-70b-versatile"

_PROMPT_TEMPLATE = """\
You are a senior QA engineer. Given the following Jira issue, generate a comprehensive Test Plan.

---
Issue Key : {key}
Type      : {issue_type}
Priority  : {priority}
Status    : {status}
Assignee  : {assignee}
Summary   : {summary}

Description:
{description}
---

Generate a formal Test Plan that includes:
1. **Objective** — What is being tested and why
2. **Scope** — Features in scope and out of scope
3. **Test Strategy** — Approach (unit, integration, E2E, etc.)
4. **Test Cases** — Minimum 5, each with:
   - Test Case ID ({key}-TC-001, etc.)
   - Title
   - Preconditions
   - Steps (numbered)
   - Expected Result
5. **Entry & Exit Criteria**
6. **Risks & Mitigations**

Use formal, professional tone. Format test cases using Steps + Expected Result (not Gherkin).\
"""


def generate_test_plan(issue: dict, groq_api_key: str) -> str:
    """Generate a Markdown test plan from a normalized Jira issue dict."""
    prompt = _PROMPT_TEMPLATE.format(**issue)
    client = Groq(api_key=groq_api_key)
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return resp.choices[0].message.content
