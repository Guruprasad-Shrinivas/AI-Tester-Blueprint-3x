# AGENTS — AI Coding Agent Instructions

Purpose: give AI coding agents concise, actionable guidance for working in this repository. This file is minimal by design — link to existing docs rather than copy them.

Focused area: MCP — the agent should prioritize tasks related to the `MCP` topic when asked, and ask the human for any ambiguous MCP acronym meaning before making wide changes.

Quick start
- **Python env**: Use a virtual environment. Do not edit the bundled `Lib/` directory (it contains vendored site-packages).
- **Run main scripts**: `python app.py` or run helper scripts like `generate_test_plan.py` and `convert_to_html.py` from the repo root.

Key files
- `app.py`: main entry/experiment script.
- `generate_test_plan.py`: generates test plans (agents may update or extend its logic when asked).
- `convert_to_html.py`: converts markdown outputs to HTML.
- `templates/index.html`: front-end template used by conversion scripts.
- `test_plan_output.md` / `test_plan_output.html`: example outputs.

Agent conventions
- **Minimal edits**: Prefer small, focused changes and preserve project style.
- **Link, don't embed**: If an agent needs documentation, link to existing markdown in the repo rather than copying it.
- **Ask before large refactors**: For refactors touching >1 top-level file or changing public APIs, request human confirmation.
- **Don't modify `Lib/`**: Treat the `Lib/` directory as read-only vendor code unless explicitly tasked.
- **Commits & messages**: Use clear, one-line summary followed by a short body describing intent.

MCP-specific guidance
- If `MCP` is mentioned without definition, ask the user whether it refers to: a module/component name, a model/config prompt, or a milestone/plan. Do not assume.
- For MCP tasks: locate related files (search for `MCP`, `mcp`, or the human-supplied identifier), propose a short plan, and wait for approval before implementing.
- Provide runnable examples and tests when implementing new MCP functionality. Include a brief README snippet describing how to exercise it.

Suggested next customizations
- Create a small skill or prompt for `create-mcp-plan` that scaffolds MCP work: finds related files, creates TODOs, and generates a minimal test harness.

Links
- Project files: see root files such as `app.py`, `generate_test_plan.py`, `convert_to_html.py` and `templates/index.html`.

If this looks good, I can: create a `/.github/copilot-instructions.md` variant, add a dedicated `skills/mcp/` prompt, or scaffold the suggested `create-mcp-plan` skill.
