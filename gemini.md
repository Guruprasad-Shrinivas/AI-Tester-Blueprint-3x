# Project Constitution — Jira Test Plan Generator

---

## Data Schema

### Input (from user via web form)
```json
{
  "issue_key": "KAN-1"
}
```

### Jira Payload (fetched from API)
```json
{
  "key": "KAN-1",
  "summary": "string",
  "description": "string (plain text extracted from ADF)",
  "issue_type": "string",
  "priority": "string",
  "status": "string",
  "assignee": "string"
}
```

### Output (Test Plan)
```json
{
  "issue_key": "KAN-1",
  "summary": "string",
  "test_plan_markdown": "string (full markdown from Groq)"
}
```

---

## Behavioral Rules
- Minimum **5 test cases** per issue
- Format: **Steps + Expected Result** (not Gherkin)
- Tone: **Formal / professional**
- Test case IDs follow pattern: `{ISSUE_KEY}-TC-00N`
- Always include: Objective, Scope, Test Strategy, Test Cases, Entry/Exit Criteria, Risks & Mitigations
- Do NOT invent data not present in the Jira issue

---

## Architectural Invariants
- Framework: **Flask** (Python, localhost)
- LLM: **Groq** (`llama-3.3-70b-versatile`)
- Jira: REST API v3 (`/rest/api/3/issue/{key}`)
- Config: all secrets loaded from `.env` via `python-dotenv`
- Single-page app: form + results rendered on the same page
- Any Jira issue ID can be entered — not hardcoded to KAN-1
