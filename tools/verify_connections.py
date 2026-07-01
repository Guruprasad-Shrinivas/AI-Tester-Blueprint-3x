"""
Phase 2 - Link verification.
Run to confirm Jira and Groq credentials are valid before building.
Exit 0 = all green. Exit 1 = at least one connection failed.
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, r"c:\AI\3x\Chatpter_3_BLAST_FramWork\Lib\site-packages")

import os
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=r"c:\AI\3x\Chatpter_3_BLAST_FramWork\.env")

GROQ_KEY       = os.getenv("GROQ_KEY")
JIRA_EMAIL     = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_URL       = os.getenv("JIRA_URL")

results = {}

# -- Jira handshake ----------------------------------------------------------
print("[ Jira ] Testing connection...")
try:
    resp = requests.get(
        f"{JIRA_URL}/rest/api/3/project",
        auth=(JIRA_EMAIL, JIRA_API_TOKEN),
        headers={"Accept": "application/json"},
        timeout=10,
    )
    resp.raise_for_status()
    projects = resp.json()
    keys = [p.get("key") for p in projects[:3]]
    print(f"[ Jira ] OK -- authenticated. Projects visible: {keys}")
    results["jira"] = True
except requests.HTTPError as e:
    code = e.response.status_code if e.response is not None else "?"
    print(f"[ Jira ] FAILED -- HTTP {code}: {e}")
    results["jira"] = False
except Exception as e:
    print(f"[ Jira ] FAILED -- {e}")
    results["jira"] = False

# -- Groq handshake ----------------------------------------------------------
print("[ Groq ] Testing connection...")
try:
    from groq import Groq
    client = Groq(api_key=GROQ_KEY)
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Reply with the single word: OK"}],
        max_tokens=5,
        temperature=0,
    )
    reply = resp.choices[0].message.content.strip()
    print(f"[ Groq ] OK -- model replied: {reply}")
    results["groq"] = True
except Exception as e:
    print(f"[ Groq ] FAILED -- {e}")
    results["groq"] = False

# -- Summary -----------------------------------------------------------------
print("\n-- Link Verification Summary --")
all_ok = True
for service, ok in results.items():
    status = "[PASS]" if ok else "[FAIL]"
    print(f"  {status}  {service.upper()}")
    if not ok:
        all_ok = False

if all_ok:
    print("\nAll connections verified. Safe to proceed to Phase 3.")
    sys.exit(0)
else:
    print("\nOne or more connections failed. Fix credentials in .env before proceeding.")
    sys.exit(1)
