# task_plan.md — BLAST Test Case Creation

## Goal
Lightweight React app that fetches a Jira issue and generates 3 test cases via GROQ.

## Phases
- [x] Phase 0: Initialization
- [x] Phase 1: Blueprint — approved
- [x] Phase 2: Link — Jira ✅ + GROQ ✅ (re-verified with new token)
- [x] Phase 3: Architect — 3-layer build complete
- [x] Phase 4: Stylize — React UI complete, end-to-end tested
- [ ] Phase 5: Trigger — Vercel deployment (pending user action)

## How to Run (Local)

### Terminal 1 — Backend API
```
cd Chapter_3(a)_B.L.A.S.T_FrameWork-TestCaseCreation
py api/index.py
# Runs on http://localhost:5001
```

### Terminal 2 — Frontend
```
cd Chapter_3(a)_B.L.A.S.T_FrameWork-TestCaseCreation/frontend
npm run dev
# Runs on http://localhost:3000
```

### First Use
1. Open http://localhost:3000
2. Click ⚙ Settings
3. Enter your Jira URL, email, new API token, GROQ key → Save
4. Type KAN-5 → click ▶ Generate Test Cases
5. Gets: Happy Path · Negative · Edge Case

## File Structure
```
├── .env                       # Server-side API keys (new token active)
├── api/index.py               # Layer 2: Flask API (port 5001)
├── tools/
│   ├── jira_tool.py           # Layer 3: Jira fetcher
│   ├── llm_tool.py            # Layer 3: GROQ generator
│   └── verify_links.py        # Phase 2: Link handshake
├── architecture/
│   └── sop_test_case.md       # Layer 1: SOP
├── frontend/
│   ├── src/App.jsx            # Main shell
│   ├── src/components/
│   │   ├── SettingsPanel.jsx  # Credentials modal
│   │   └── TestCasePanel.jsx  # Issue input + TC display
│   └── src/App.css            # Full styling
├── vercel.json                # Deployment config
└── requirements.txt           # Python deps
```
