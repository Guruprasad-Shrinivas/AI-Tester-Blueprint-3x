"""
Layer 2: Navigation — Flask API for Test Case Creator.
Self-contained for Vercel deployment (no local tool imports).
Reads credentials from: UI settings → os.environ (Vercel) → .env file (local dev).
"""
import os
import sys
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests as req_lib
from groq import Groq

app = Flask(__name__)
CORS(app)

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ── Credential resolution: UI → os.environ → .env file ──────────
def _read_env_file() -> dict:
    env = {}
    try:
        with open(os.path.join(_ROOT, ".env"), encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, _, v = line.partition("=")
                    env[k.strip()] = v.strip()
    except Exception:
        pass
    return env


def _get_cred(key: str, settings: dict = None, settings_key: str = None) -> str:
    """Priority: UI setting → os.environ → .env file."""
    if settings and settings_key:
        ui_val = (settings.get(settings_key) or "").strip()
        if ui_val:
            return ui_val
    env_val = os.environ.get(key, "").strip()
    if env_val:
        return env_val
    return _read_env_file().get(key, "")


# ── Jira fetch (inlined from tools/jira_tool.py) ─────────────────
def _extract_text(node) -> str:
    if not node:
        return ""
    if isinstance(node, str):
        return node
    text = node.get("text", "")
    for child in node.get("content", []):
        text += _extract_text(child)
    if node.get("type") in ("paragraph", "heading", "listItem", "bulletList", "orderedList"):
        text += "\n"
    return text


def fetch_issue(issue_key, jira_url, jira_email, jira_token):
    url  = f"{jira_url.rstrip('/')}/rest/api/3/issue/{issue_key}"
    cred = base64.b64encode(f"{jira_email}:{jira_token}".encode()).decode()
    resp = req_lib.get(
        url,
        headers={"Accept": "application/json", "Authorization": f"Basic {cred}"},
        timeout=10,
    )
    resp.raise_for_status()
    raw    = resp.json()
    fields = raw.get("fields", {})
    return {
        "key":         raw["key"],
        "summary":     fields.get("summary", ""),
        "description": _extract_text(fields.get("description") or {}).strip() or "No description provided.",
        "issue_type":  (fields.get("issuetype") or {}).get("name", "Unknown"),
        "priority":    (fields.get("priority")  or {}).get("name", "Unknown"),
        "status":      (fields.get("status")    or {}).get("name", "Unknown"),
        "assignee":    (fields.get("assignee")  or {}).get("displayName", "Unassigned"),
    }


# ── GROQ generation (inlined from tools/llm_tool.py) ─────────────
_PROMPT = """You are a senior QA engineer. Given the Jira issue below, generate exactly 3 test cases.

---
Issue Key : {key}
Type      : {issue_type}
Priority  : {priority}
Status    : {status}
Assignee  : {assignee}
Summary   : {summary}

Description:
{description}
---

Generate exactly 3 test cases using this exact format:

---

### {key}-TC-001 — Happy Path
**Title:** [concise descriptive title]
**Type:** Happy Path
**Priority:** High
**Preconditions:**
- [precondition 1]
**Steps:**
1. [step]
2. [step]
3. [step]
**Expected Result:** [what should happen]

---

### {key}-TC-002 — Negative Test
**Title:** [concise descriptive title]
**Type:** Negative
**Priority:** High
**Preconditions:**
- [precondition 1]
**Steps:**
1. [step]
2. [step]
**Expected Result:** [what should happen — error/rejection]

---

### {key}-TC-003 — Edge Case
**Title:** [concise descriptive title]
**Type:** Edge Case
**Priority:** Medium
**Preconditions:**
- [precondition 1]
**Steps:**
1. [step]
2. [step]
**Expected Result:** [boundary/unusual outcome]

---

Be specific, professional, and actionable. Use the exact issue context above."""


def generate_test_cases(issue, groq_key, model="llama-3.3-70b-versatile"):
    client = Groq(api_key=groq_key)
    resp   = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": _PROMPT.format(**issue)}],
        temperature=0.3,
    )
    return resp.choices[0].message.content


# ── Routes ────────────────────────────────────────────────────────
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status":         "ok",
        "service":        "test-case-creator",
        "jira_url_set":   bool(_get_cred("JIRA_URL")),
        "jira_token_set": bool(_get_cred("JIRA_API_TOKEN")),
        "groq_key_set":   bool(_get_cred("GROQ_KEY")),
    })


@app.route("/api/generate", methods=["POST"])
def generate():
    data     = request.get_json(force=True) or {}
    issue_id = (data.get("issue_id") or "").strip().upper()
    settings = data.get("settings") or {}

    if not issue_id:
        return jsonify({"error": "Issue ID is required."}), 400

    jira_url   = _get_cred("JIRA_URL",       settings, "jira_url")
    jira_email = _get_cred("JIRA_EMAIL",      settings, "jira_email")
    jira_token = _get_cred("JIRA_API_TOKEN",  settings, "jira_token")
    groq_key   = _get_cred("GROQ_KEY",        settings, "groq_key")
    model      = (settings.get("model") or "").strip() or "llama-3.3-70b-versatile"

    if not jira_token:
        return jsonify({"error": "Jira API token missing. Set in Settings or Vercel env vars."}), 400
    if not groq_key:
        return jsonify({"error": "GROQ API key missing. Set in Settings or Vercel env vars."}), 400

    try:
        issue = fetch_issue(issue_id, jira_url, jira_email, jira_token)
    except req_lib.HTTPError as e:
        code = e.response.status_code if e.response is not None else "?"
        if code in (401, 403):
            return jsonify({"error": f"Jira access denied for '{issue_id}'. Check token in Settings."}), 502
        if code == 404:
            return jsonify({"error": f"Issue '{issue_id}' not found in Jira."}), 404
        return jsonify({"error": f"Jira error {code} for '{issue_id}'."}), 502
    except Exception as e:
        return jsonify({"error": f"Jira connection failed: {e}"}), 502

    try:
        test_cases_md = generate_test_cases(issue, groq_key, model)
    except Exception as e:
        return jsonify({"error": f"GROQ generation failed: {e}"}), 502

    return jsonify({"issue": issue, "test_cases_md": test_cases_md})


if __name__ == "__main__":
    print("🚀 Test Case Creator API — http://localhost:5001")
    print(f"   JIRA_URL  : {_get_cred('JIRA_URL') or '(not set)'}")
    print(f"   JIRA_TOKEN: {'✅' if _get_cred('JIRA_API_TOKEN') else '❌ MISSING'}")
    print(f"   GROQ_KEY  : {'✅' if _get_cred('GROQ_KEY') else '❌ MISSING'}")
    app.run(debug=False, port=5001, use_reloader=False)
