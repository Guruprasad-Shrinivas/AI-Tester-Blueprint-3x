# SOP: Test Plan Generation

## Goal
Given a normalized Jira issue dict, produce a structured Test Plan in Markdown using Groq LLM.

## Inputs
| Field | Type | Source |
|---|---|---|
| `issue` | dict | Output of `jira_tool.fetch_issue()` |
| `GROQ_KEY` | string | `.env` |

## Tool
`tools/llm_tool.py` → `generate_test_plan(issue)`

## Steps
1. Extract fields from issue dict (key, summary, description, type, priority, status, assignee)
2. Build structured prompt (see Prompt Template below)
3. Call Groq `llama-3.3-70b-versatile` with `temperature=0.3`
4. Return raw markdown string

## Prompt Template
```
You are a senior QA engineer. Given the following Jira issue, generate a comprehensive Test Plan.
[issue fields]
Generate a formal Test Plan that includes:
1. Objective
2. Scope
3. Test Strategy
4. Test Cases (minimum 5) — each with:
   - ID: {ISSUE_KEY}-TC-001
   - Title, Preconditions, Steps (numbered), Expected Result
5. Entry & Exit Criteria
6. Risks & Mitigations
Format: Steps + Expected Result (not Gherkin). Tone: formal/professional.
```

## Output
- Raw Markdown string
- Caller (app.py) converts to HTML via `markdown` library with `tables` extension

## Behavioral Rules (from gemini.md)
- Minimum 5 test cases
- Format: Steps + Expected Result only
- Test case IDs: `{ISSUE_KEY}-TC-00N`
- Do NOT invent data not in the Jira issue
- Tone: formal, professional

## Edge Cases
- Empty description: pass `"No description provided."` to avoid blank prompt section
- LLM timeout: surface as generic error to user
