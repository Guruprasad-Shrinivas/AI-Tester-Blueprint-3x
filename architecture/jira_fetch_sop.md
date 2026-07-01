# SOP: Jira Issue Fetch

## Goal
Retrieve a single Jira issue by key and return a normalized Python dict for downstream use.

## Inputs
| Field | Type | Source |
|---|---|---|
| `issue_key` | string | User form input (e.g. `KAN-1`) |
| `JIRA_URL` | string | `.env` |
| `JIRA_EMAIL` | string | `.env` |
| `JIRA_API_TOKEN` | string | `.env` |

## Tool
`tools/jira_tool.py` → `fetch_issue(issue_key)`

## Steps
1. Build URL: `{JIRA_URL}/rest/api/3/issue/{issue_key}`
2. Call GET with Basic Auth (email + token) and `Accept: application/json`
3. On HTTP error: raise with status code for caller to handle
4. On success: extract and return normalized fields (see Output)

## Output (normalized dict)
```json
{
  "key": "KAN-1",
  "summary": "string",
  "description": "string (plain text, ADF extracted)",
  "issue_type": "string",
  "priority": "string",
  "status": "string",
  "assignee": "string"
}
```

## Edge Cases
- ADF description: recursively walk `content[]` nodes; append `\n` after paragraph/heading/list nodes
- Null fields (`assignee`, `priority`): default to `"Unassigned"` / `"Unknown"`
- 401: invalid credentials → surface to user as "Access denied"
- 404: issue not found → surface to user as "Issue not found"

## Discoveries
- Atlassian Document Format (ADF) requires recursive text extraction — do not read `.get("text")` at top level only
- `/rest/api/3/project` is the reliable auth-check endpoint; `/myself` may return 401 on some instances
