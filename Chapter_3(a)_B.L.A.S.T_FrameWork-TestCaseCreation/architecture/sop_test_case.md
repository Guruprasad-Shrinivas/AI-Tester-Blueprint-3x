# SOP: Test Case Creator — Architecture Layer 1

## Goal
Fetch a Jira issue by ID and generate 3 structured test cases using GROQ LLM.

## Tool Chain (in order)
1. `tools/jira_tool.py :: fetch_issue(issue_key, jira_url, jira_email, jira_token)`
   - Calls Jira REST API v3: `GET /rest/api/3/issue/{key}`
   - Extracts: key, summary, description (ADF→text), issue_type, priority, status, assignee
   - Raises `requests.HTTPError` on 401/403/404

2. `tools/llm_tool.py :: generate_test_cases(issue, groq_key, model)`
   - Sends structured prompt to GROQ chat completions
   - Returns raw markdown string with 3 test cases
   - Temperature: 0.3 (deterministic output)

3. `api/index.py :: POST /api/generate`
   - Merges settings from request body with .env fallback
   - Calls tool chain in order
   - Returns JSON: {issue, test_cases_md}

## Edge Cases & Rules
- If JIRA_URL has trailing slash → strip it (`rstrip('/')`)
- If description is Atlassian Document Format (ADF) → recursive text extraction
- If model fails → self-annealing: try `llama-3.3-70b-versatile` fallback
- 401/403 → "Access denied — check Jira credentials"
- 404 → "Issue '{key}' not found in Jira"
- GROQ timeout → surface error to UI, do not retry silently

## Self-Annealing: .env Loading Bug (Fixed)
- **Problem**: `load_dotenv()` at Flask startup sets `os.environ` once. Werkzeug debug reloader child process loaded old cached code, ignoring the new token in `.env`. Result: `os.getenv("JIRA_API_TOKEN")` returned blank → Jira 404.
- **Fix**: Replaced `load_dotenv` + `os.getenv` with `_read_env()` — a per-request direct file reader that parses `.env` on every call using `line.partition("=")` (handles `=` inside values correctly).
- **Fix 2**: Disabled Werkzeug reloader (`use_reloader=False`, `debug=False`) so only ONE Python process runs, and the correct code version is always active.
- **Rule added**: Never use `load_dotenv` + `os.getenv` for credentials in Flask — use `_read_env()` per-request instead.

## Known Constraints
- Jira API search/jql (GET) deprecated → use POST /search/jql or direct /issue/{key}
- GROQ free tier has rate limits: ~30 req/min on llama-3.3-70b-versatile
