"""
Phase 2: L - Link Verification (Handshake script).
Run this before full build to confirm both APIs are reachable.
Usage: python tools/verify_links.py
"""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(_ROOT, ".env"), override=True)

import requests
from groq import Groq

GROQ_KEY       = os.getenv("GROQ_KEY")
JIRA_EMAIL     = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_URL       = os.getenv("JIRA_URL")

print("=" * 50)
print("Phase 2: L — Link Verification")
print("=" * 50)

# ── Jira Handshake ──
print("\n[1/2] Jira API...")
try:
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/issue/KAN-5"
    import base64
    cred = base64.b64encode(f"{JIRA_EMAIL}:{JIRA_API_TOKEN}".encode()).decode()
    r = requests.get(url, headers={"Accept": "application/json",
                     "Authorization": f"Basic {cred}"}, timeout=10)
    r.raise_for_status()
    data = r.json()
    print(f"  ✅ Connected. Found: {data['key']} — {data['fields']['summary']}")
except Exception as e:
    print(f"  ❌ FAILED: {e}")

# ── GROQ Handshake ──
print("\n[2/2] GROQ API...")
try:
    client = Groq(api_key=GROQ_KEY)
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Reply with exactly: GROQ_OK"}],
        max_tokens=10,
        temperature=0,
    )
    reply = resp.choices[0].message.content.strip()
    print(f"  ✅ Connected. Model reply: {reply}")
except Exception as e:
    print(f"  ❌ FAILED: {e}")

print("\n" + "=" * 50)
print("Link verification complete.")
