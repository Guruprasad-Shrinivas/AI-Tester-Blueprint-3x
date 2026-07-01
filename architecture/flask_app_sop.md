# SOP: Flask Navigation Layer

## Goal
Serve the web UI, route user input through the tool chain, and render the result.

## Layer Role
This is **Layer 2 (Navigation)** — it routes data between tools, does not contain business logic.

## Entry Point
`app.py` → Flask app on `localhost:5000` (local) / Vercel (production)

## Request Flow
```
User (browser)
  --> POST / {issue_key}
  --> app.py: validate input
  --> tools/jira_tool.py: fetch_issue(issue_key)
  --> tools/llm_tool.py: generate_test_plan(issue)
  --> markdown.markdown(plan_markdown)
  --> render_template("index.html", test_plan_html=...)
  --> User sees rendered Test Plan
```

## Routes
| Method | Path | Action |
|---|---|---|
| GET | `/` | Render empty form |
| POST | `/` | Run full pipeline, render result |

## Error Handling
| Error | User Message |
|---|---|
| `requests.HTTPError 401/403` | "Access denied for issue '{key}'" |
| `requests.HTTPError 404` | "Issue '{key}' not found" |
| Any other exception | "Unexpected error: {message}" |

## Vercel Deployment
- Entry: `api/index.py` imports Flask `app` as `handler`
- Env vars injected by Vercel (no `.env` file needed in production)
- Template folder: `templates/` at project root (resolved by Flask via `app.py` location)
