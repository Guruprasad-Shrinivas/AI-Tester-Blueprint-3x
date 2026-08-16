"""
Layer 3 Tool: GROQ Test Case Generator.
Atomic, testable. Generates 3 test cases per Jira issue.
SOP: architecture/sop_test_case.md
"""
from groq import Groq

_DEFAULT_MODEL = "llama-3.3-70b-versatile"

_PROMPT_TEMPLATE = """You are a senior QA engineer. Given the Jira issue below, generate exactly 3 test cases.

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

Generate exactly 3 test cases using this exact format:

---

### {key}-TC-001 — Happy Path
**Title:** [concise descriptive title]
**Type:** Happy Path
**Priority:** High
**Preconditions:**
- [precondition 1]
**Steps:**
1. [step]
2. [step]
3. [step]
**Expected Result:** [what should happen]

---

### {key}-TC-002 — Negative Test
**Title:** [concise descriptive title]
**Type:** Negative
**Priority:** High
**Preconditions:**
- [precondition 1]
**Steps:**
1. [step]
2. [step]
**Expected Result:** [what should happen — error/rejection]

---

### {key}-TC-003 — Edge Case
**Title:** [concise descriptive title]
**Type:** Edge Case
**Priority:** Medium
**Preconditions:**
- [precondition 1]
**Steps:**
1. [step]
2. [step]
**Expected Result:** [boundary/unusual outcome]

---

Be specific, professional, and actionable. Use the exact issue context above."""


def generate_test_cases(issue: dict, groq_key: str, model: str = _DEFAULT_MODEL) -> str:
    """
    Generate 3 test cases for a Jira issue using GROQ.
    Returns raw markdown string.
    """
    prompt = _PROMPT_TEMPLATE.format(**issue)

    client = Groq(api_key=groq_key)
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return resp.choices[0].message.content
