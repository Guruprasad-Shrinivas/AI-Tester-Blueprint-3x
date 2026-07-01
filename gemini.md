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
- Format: **Steps + Expected Result** (not Gherkin, not BDD) — user confirmed 2026-06-29
- Tone: **Formal / professional**
- Test case IDs follow pattern: `{ISSUE_KEY}-TC-00N`
- Always include: Objective, Scope, Test Strategy, Test Cases, Entry/Exit Criteria, Risks & Mitigations
- Do NOT invent data not present in the Jira issue
- Source of truth: **Jira REST API only** — no manual input, no Confluence, no GitHub
- Delivery: **Browser display only** — no PDF export, no Jira write-back, no email/Slack

---

## Architectural Invariants
- Framework: **Flask** (Python, localhost)
- LLM: **Groq** (`llama-3.3-70b-versatile`)
- Jira: REST API v3 (`/rest/api/3/issue/{key}`)
- Config: all secrets loaded from `.env` via `python-dotenv`
- Single-page app: form + results rendered on the same page
- Any Jira issue ID can be entered — not hardcoded to KAN-1
- 3-layer A.N.T. architecture: `architecture/` (SOPs) → `app.py` (navigation) → `tools/` (atomic scripts)
- Vercel entry: `api/index.py` wraps Flask `app` as `handler`

---

## File Structure
```
├── gemini.md                          # Project Constitution (this file)
├── .env                               # Secrets (never committed)
├── app.py                             # Layer 2: Navigation (Flask routing)
├── api/index.py                       # Vercel serverless entry point
├── requirements.txt                   # Python dependencies
├── vercel.json                        # Vercel build config
├── architecture/
│   ├── jira_fetch_sop.md              # SOP: Jira API fetch
│   ├── test_plan_generation_sop.md    # SOP: Groq LLM generation
│   └── flask_app_sop.md              # SOP: Navigation layer
├── tools/
│   ├── jira_tool.py                   # Layer 3: Jira fetch (atomic)
│   ├── llm_tool.py                    # Layer 3: Groq generation (atomic)
│   └── verify_connections.py          # Phase 2: Link verification
├── templates/
│   └── index.html                     # UI: single-page form + results
└── .tmp/                              # Ephemeral intermediates (not committed)
```

---

## Maintenance Log

### 2026-07-02 — BLAST Full Run
- Completed all 5 BLAST phases
- Phase 2 (Link): Jira auth verified via `/rest/api/3/project` (200 OK); `/myself` returns 401 on this instance (known quirk — do not use for auth check)
- Phase 3 (Architect): Refactored monolithic `app.py` into 3-layer A.N.T. architecture
- Phase 4 (Stylize): Added copy-to-clipboard button and animated spinner to UI
- Phase 5 (Trigger): Deployed to Vercel (`testplanbuddy-delta.vercel.app`); pushed to GitHub branch `AI-Tester-Blueprint-3x`
