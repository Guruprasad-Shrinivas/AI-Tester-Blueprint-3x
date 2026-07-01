"""
Layer 3 Tool: Jira Issue Fetch
Atomic, testable. No Flask imports. No LLM calls.
SOP: architecture/jira_fetch_sop.md
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "Lib", "site-packages"))

import requests


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


def fetch_issue(issue_key: str, jira_url: str, email: str, token: str) -> dict:
    """Fetch a Jira issue and return a normalized dict. Raises requests.HTTPError on failure."""
    url = f"{jira_url}/rest/api/3/issue/{issue_key}"
    resp = requests.get(
        url,
        auth=(email, token),
        headers={"Accept": "application/json"},
        timeout=10,
    )
    resp.raise_for_status()
    raw = resp.json()
    fields = raw.get("fields", {})
    return {
        "key":        raw["key"],
        "summary":    fields.get("summary", ""),
        "description": _extract_text(fields.get("description") or {}).strip() or "No description provided.",
        "issue_type": (fields.get("issuetype") or {}).get("name", "Unknown"),
        "priority":   (fields.get("priority")  or {}).get("name", "Unknown"),
        "status":     (fields.get("status")    or {}).get("name", "Unknown"),
        "assignee":   (fields.get("assignee")  or {}).get("displayName", "Unassigned"),
    }
