# gemini.md — Project Constitution (LAW)

> Only update when: schema changes, rule added, architecture modified.

## Status: BLUEPRINT APPROVED → BUILD IN PROGRESS

---

## Data Schema (CONFIRMED)

### API Request — POST /api/generate
```json
{
  "issue_id": "KAN-5",
  "settings": {
    "jira_url":   "https://prasadpachuu.atlassian.net",
    "jira_email": "prasad.pachuu@gmail.com",
    "jira_token": "ATATT3x...",
    "groq_key":   "gsk_...",
    "model":      "llama-3.3-70b-versatile"
  }
}
```

### Jira Fetched Payload (Layer 3 — jira_tool.py output)
```json
{
  "key":         "KAN-5",
  "summary":     "string",
  "description": "string",
  "issue_type":  "string",
  "priority":    "string",
  "status":      "string",
  "assignee":    "string"
}
```

### API Response — success
```json
{
  "issue":         { "key": "KAN-5", "summary": "...", "..." : "..." },
  "test_cases_md": "### Test Case KAN-5-TC-001\n..."
}
```

### API Response — error
```json
{ "error": "human-readable error string" }
```

### Test Case Output Shape (per issue: 3 cases)
```
TC-001 → Happy Path
TC-002 → Negative Test
TC-003 → Edge Case

Each has: TC-ID, Title, Type, Priority, Preconditions, Steps (numbered), Expected Result
```

---

## Behavioral Rules

1. Settings saved to localStorage key `blast_tc_settings`
2. .env values are fallback when Settings panel is empty
3. Model is configurable — default: `llama-3.3-70b-versatile`
4. Always generate 3 test cases per issue (happy, negative, edge)
5. Test Case IDs: `{ISSUE_KEY}-TC-001` format
6. Never hardcode credentials in frontend code

## Architectural Invariants

- Layer 1: `architecture/sop_test_case.md` — SOP
- Layer 2: `api/index.py` — Flask routing (no business logic)
- Layer 3: `tools/jira_tool.py` + `tools/llm_tool.py` — atomic engines
- Frontend: `frontend/src/` — React (Vite)
- Secrets: `.env` + localStorage (never committed to git)
