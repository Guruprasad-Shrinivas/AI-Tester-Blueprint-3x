"""
Layer 3 Tool: Jira Issue Fetcher.
Atomic, testable. No side effects beyond HTTP GET.
SOP: architecture/sop_test_case.md
"""
import requests


def _extract_text(node) -> str:
    """Recursively extract plain text from Jira Atlassian Document Format (ADF)."""
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


def fetch_issue(issue_key: str, jira_url: str, jira_email: str, jira_token: str) -> dict:
    """
    Fetch a single Jira issue and return a clean dict.
    Raises requests.HTTPError on 4xx/5xx responses.
    """
    url = f"{jira_url.rstrip('/')}/rest/api/3/issue/{issue_key}"
    import base64
    cred = base64.b64encode(f"{jira_email}:{jira_token}".encode()).decode()
    resp = requests.get(
        url,
        headers={"Accept": "application/json", "Authorization": f"Basic {cred}"},
        timeout=10,
    )
    resp.raise_for_status()

    raw = resp.json()
    fields = raw.get("fields", {})

    return {
        "key":        raw["key"],
        "summary":    fields.get("summary", ""),
        "description": _extract_text(fields.get("description") or {}).strip()
                       or "No description provided.",
        "issue_type": (fields.get("issuetype") or {}).get("name", "Unknown"),
        "priority":   (fields.get("priority") or {}).get("name", "Unknown"),
        "status":     (fields.get("status") or {}).get("name", "Unknown"),
        "assignee":   (fields.get("assignee") or {}).get("displayName", "Unassigned"),
    }
