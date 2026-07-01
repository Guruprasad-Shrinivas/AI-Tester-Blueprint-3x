# Findings

## Project: Jira Test Plan Generator

---

## Research
- Jira REST API v3 used for issue fetch: `/rest/api/3/issue/{key}`
- Groq LLM (`llama-3.3-70b-versatile`) used for test plan generation
- Flask serves the single-page web app on localhost:5000

## Constraints
- Source of truth is Jira only — no other input sources
- Output is browser-only — no file export or Jira write-back
- Test case format locked to Steps + Expected Result (not Gherkin/BDD)
- All secrets (JIRA_EMAIL, JIRA_API_TOKEN, JIRA_URL, GROQ_KEY) must be in `.env`

## Discoveries
- Jira description uses Atlassian Document Format (ADF); requires recursive text extraction
- ADF node types (paragraph, heading, listItem) must be handled to produce readable plain text
