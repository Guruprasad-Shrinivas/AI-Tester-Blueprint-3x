# Findings

## Confirmed
- GROQ model `llama-3.3-70b-versatile` works and generates high-quality test cases
- Jira issues available: KAN-1 through KAN-5 (KAN-6+ return 404)
- KAN-5 summary: "Implement Muco (TaxPlanCode is 1247Q) Enhancement FXXX form"
- Python 3.14 + requests `auth=` tuple sends malformed auth for this Jira instance — use explicit base64 header

## Architecture Decisions
- API on port 5001 (5000 conflicts with Chapter_3 BLAST app)
- Credentials flow: .env (server default) OR Settings panel (user override via localStorage → request body)
- react-markdown for test case rendering (lighter than custom parser)

## Known Constraints
- Jira API search/jql (GET) deprecated → use POST or direct /issue/{key}
- GROQ free tier: ~30 req/min on llama-3.3-70b-versatile
- .env JIRA_API_TOKEN tends to be reset by VS Code formatter — use Settings panel as primary credentials method

## Credential History
- Token v1: ended =CA97FB10 (replaced by user)
- Token v2: ended =6F82A9B5 (current, verified working)
- B.L.A.S.T.md v2: planning file is `task_plan.md` (not task_case.md)

## Self-Annealing Log
1. [Phase 2] requests auth=tuple → 404 → Fixed: explicit Authorization header
2. [Phase 2] blank JIRA_API_TOKEN in .env → app still works via Settings panel credentials
3. [Phase 3] Port 5000 conflict with Chapter_3 → moved to port 5001
