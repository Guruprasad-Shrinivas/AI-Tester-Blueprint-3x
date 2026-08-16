"""
Layer 3 Tool: Fetch Jira issue from .env credentials and generate
comprehensive Excel test cases (positive + negative) via GROQ.
"""
import os, sys, json, base64, re
import requests
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from groq import Groq

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ── 1. Read .env ────────────────────────────────────────────────
def read_env():
    env = {}
    with open(os.path.join(_ROOT, ".env"), encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and "=" in line and not line.startswith("#"):
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip()
    return env


# ── 2. Fetch Jira Issue ─────────────────────────────────────────
def fetch_issue(issue_key, env):
    url   = f"{env['JIRA_URL'].rstrip('/')}/rest/api/3/issue/{issue_key}"
    cred  = base64.b64encode(
        f"{env['JIRA_EMAIL']}:{env['JIRA_API_TOKEN']}".encode()
    ).decode()
    resp  = requests.get(
        url,
        headers={"Accept": "application/json", "Authorization": f"Basic {cred}"},
        timeout=15,
    )
    resp.raise_for_status()
    raw    = resp.json()
    fields = raw.get("fields", {})

    def text(node):
        if not node: return ""
        if isinstance(node, str): return node
        out = node.get("text", "")
        for c in node.get("content", []):
            out += text(c)
        if node.get("type") in ("paragraph","heading","listItem","bulletList","orderedList"):
            out += "\n"
        return out

    return {
        "key":         raw["key"],
        "summary":     fields.get("summary", ""),
        "description": text(fields.get("description") or {}).strip() or "No description.",
        "issue_type":  (fields.get("issuetype") or {}).get("name", "Unknown"),
        "priority":    (fields.get("priority")  or {}).get("name", "Unknown"),
        "status":      (fields.get("status")    or {}).get("name", "Unknown"),
        "assignee":    (fields.get("assignee")  or {}).get("displayName", "Unassigned"),
    }


# ── 3. Generate Test Cases via GROQ ────────────────────────────
PROMPT = """You are a senior QA engineer. Based on the Jira issue below, generate a COMPREHENSIVE test case suite.

---
Issue Key : {key}
Type      : {issue_type}
Priority  : {priority}
Summary   : {summary}
Description:
{description}
---

Generate test cases in EXACTLY this JSON format (no extra text, pure JSON):

{{
  "test_cases": [
    {{
      "id":                 "TC-001",
      "title":              "string",
      "type":               "Positive | Negative | Edge Case | Boundary | Error Handling",
      "category":           "Functional | UI | Integration | Performance | Security",
      "priority":           "Critical | High | Medium | Low",
      "preconditions":      ["string", ...],
      "steps":              ["Step 1: ...", "Step 2: ...", ...],
      "expected_result":    "string",
      "actual_result":      "To be filled during execution",
      "status":             "Not Run",
      "test_data":          "string or N/A",
      "pass_fail_criteria": "string"
    }}
  ]
}}

Rules:
- Generate MINIMUM 3 test cases per type — all 5 types are REQUIRED:
  1. Positive (happy path) — at least 3: valid TaxPlanCode + valid entities + valid plan keys → IN result
  2. Negative — at least 4: EACH excluded entity (PRVCX, PRVQX, PRVZX, PRVTX) gets its own TC, EACH excluded plan key (721450-X2, 721451-X2, 884203-X2, 664912-X2) gets its own TC
  3. Edge Case — at least 3: empty fields, null values, mixed valid/invalid, case sensitivity
  4. Boundary — at least 2: exactly on boundary conditions, whitespace in codes
  5. Error Handling — at least 2: API timeout, unauthorized, invalid issue format
- Each test case MUST be specific to the Muco TaxPlanCode 1247Q issue context
- Use issue key prefix: {key}-TC-001, {key}-TC-002, etc.
- Be specific, professional, and actionable
- Return ONLY valid JSON, no markdown fences"""


def generate_test_cases(issue, env):
    client = Groq(api_key=env["GROQ_KEY"])
    resp   = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": PROMPT.format(**issue)}],
        temperature=0.3,
        max_tokens=6000,
    )
    raw = resp.choices[0].message.content.strip()
    # Strip markdown fences if model adds them
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$",          "", raw)
    return json.loads(raw)["test_cases"]


# ── 4. Build Excel ──────────────────────────────────────────────
TYPE_COLORS = {
    "Positive":       "E2EFDA",   # green
    "Negative":       "FCE4D6",   # red/salmon
    "Edge Case":      "FFF2CC",   # yellow
    "Boundary":       "DDEBF7",   # blue
    "Error Handling": "F4CCFF",   # purple
}
PRIORITY_COLORS = {
    "Critical": "FF0000",
    "High":     "FF7043",
    "Medium":   "FFB300",
    "Low":      "4CAF50",
}

THIN   = Side(style="thin",   color="BFBFBF")
MEDIUM = Side(style="medium", color="1F3864")
BTHIN  = Border(left=THIN,   right=THIN,   top=THIN,   bottom=THIN)
BMED   = Border(left=MEDIUM, right=MEDIUM, top=MEDIUM, bottom=MEDIUM)
WRAP_C = Alignment(horizontal="center", vertical="center", wrap_text=True)
WRAP_L = Alignment(horizontal="left",   vertical="center", wrap_text=True)
WRAP_T = Alignment(horizontal="left",   vertical="top",    wrap_text=True)


def build_excel(issue, test_cases, out_path):
    wb = openpyxl.Workbook()

    # ── Sheet 1: All Test Cases ──────────────────────────────────
    ws = wb.active
    ws.title = "All Test Cases"

    COLS = [
        ("TC ID",             14),
        ("Title",             38),
        ("Type",              16),
        ("Category",          16),
        ("Priority",          12),
        ("Preconditions",     36),
        ("Test Steps",        52),
        ("Expected Result",   38),
        ("Actual Result",     30),
        ("Status",            12),
        ("Test Data",         22),
        ("Pass/Fail Criteria",36),
    ]

    # Title banner
    ws.merge_cells(f"A1:{get_column_letter(len(COLS))}1")
    t = ws["A1"]
    t.value     = f"{issue['key']}  ·  {issue['summary']}"
    t.font      = Font(name="Calibri", bold=True, size=13, color="FFFFFF")
    t.fill      = PatternFill("solid", fgColor="0052CC")
    t.alignment = WRAP_C
    ws.row_dimensions[1].height = 30

    # Sub-banner: meta
    ws.merge_cells(f"A2:{get_column_letter(len(COLS))}2")
    m = ws["A2"]
    m.value     = (f"Type: {issue['issue_type']}   |   Priority: {issue['priority']}   |   "
                   f"Status: {issue['status']}   |   Assignee: {issue['assignee']}")
    m.font      = Font(name="Calibri", size=10, color="FFFFFF")
    m.fill      = PatternFill("solid", fgColor="1F3864")
    m.alignment = WRAP_C
    ws.row_dimensions[2].height = 18

    # Column headers
    for ci, (label, width) in enumerate(COLS, start=1):
        c = ws.cell(row=3, column=ci, value=label)
        c.font      = Font(name="Calibri", bold=True, size=10, color="FFFFFF")
        c.fill      = PatternFill("solid", fgColor="344563")
        c.alignment = WRAP_C
        c.border    = BTHIN
        ws.column_dimensions[get_column_letter(ci)].width = width
    ws.row_dimensions[3].height = 22

    # Data rows
    for ri, tc in enumerate(test_cases, start=4):
        row_color = TYPE_COLORS.get(tc.get("type", ""), "FFFFFF")
        fill      = PatternFill("solid", fgColor=row_color)

        pre   = "\n".join(f"• {p}" for p in tc.get("preconditions", []))
        steps = "\n".join(tc.get("steps", []))

        values = [
            tc.get("id", ""),
            tc.get("title", ""),
            tc.get("type", ""),
            tc.get("category", ""),
            tc.get("priority", ""),
            pre,
            steps,
            tc.get("expected_result", ""),
            tc.get("actual_result", "To be filled"),
            tc.get("status", "Not Run"),
            tc.get("test_data", "N/A"),
            tc.get("pass_fail_criteria", ""),
        ]

        for ci, val in enumerate(values, start=1):
            c = ws.cell(row=ri, column=ci, value=val)
            c.fill   = fill
            c.border = BTHIN
            c.font   = Font(name="Calibri", size=9,
                            bold=(ci == 1),
                            color=PRIORITY_COLORS.get(tc.get("priority",""), "000000") if ci == 5 else "000000")
            if ci in (1, 3, 4, 5, 9, 10):
                c.alignment = WRAP_C
            else:
                c.alignment = WRAP_T

        ws.row_dimensions[ri].height = max(
            60, 15 * max(len(steps.split("\n")), len(pre.split("\n")), 2)
        )

    ws.freeze_panes = "A4"

    # ── Sheet 2: Summary Dashboard ───────────────────────────────
    ws2 = wb.create_sheet("Summary")
    ws2.column_dimensions["A"].width = 22
    ws2.column_dimensions["B"].width = 12

    ws2.merge_cells("A1:B1")
    s = ws2["A1"]
    s.value     = "Test Case Summary"
    s.font      = Font(name="Calibri", bold=True, size=14, color="FFFFFF")
    s.fill      = PatternFill("solid", fgColor="0052CC")
    s.alignment = WRAP_C
    ws2.row_dimensions[1].height = 28

    from collections import Counter
    type_counts     = Counter(tc.get("type","")     for tc in test_cases)
    priority_counts = Counter(tc.get("priority","") for tc in test_cases)
    cat_counts      = Counter(tc.get("category","") for tc in test_cases)

    sections = [
        ("By Type",     type_counts,     TYPE_COLORS),
        ("By Priority", priority_counts, {"Critical":"FFCCCC","High":"FFE0CC","Medium":"FFF9CC","Low":"CCFFCC"}),
        ("By Category", cat_counts,      {}),
    ]

    row = 2
    for section_title, counts, color_map in sections:
        # Section header
        ws2.merge_cells(f"A{row}:B{row}")
        h = ws2[f"A{row}"]
        h.value     = section_title
        h.font      = Font(name="Calibri", bold=True, size=11, color="FFFFFF")
        h.fill      = PatternFill("solid", fgColor="1F3864")
        h.alignment = WRAP_C
        ws2.row_dimensions[row].height = 20
        row += 1

        total = sum(counts.values())
        for label, count in sorted(counts.items(), key=lambda x: -x[1]):
            pct   = f"{count/total*100:.0f}%" if total else "0%"
            color = color_map.get(label, "F2F2F2")
            for ci, val in enumerate([f"{label}  ({pct})", count], start=1):
                c = ws2.cell(row=row, column=ci, value=val)
                c.fill      = PatternFill("solid", fgColor=color)
                c.alignment = WRAP_C if ci == 2 else WRAP_L
                c.border    = BTHIN
                c.font      = Font(name="Calibri", size=10)
            ws2.row_dimensions[row].height = 18
            row += 1

        # Total row
        for ci, val in enumerate(["TOTAL", total], start=1):
            c = ws2.cell(row=row, column=ci, value=val)
            c.font      = Font(name="Calibri", bold=True, size=10)
            c.fill      = PatternFill("solid", fgColor="DEEAF1")
            c.alignment = WRAP_C if ci == 2 else WRAP_L
            c.border    = BTHIN
        ws2.row_dimensions[row].height = 18
        row += 2

    wb.save(out_path)
    print(f"✅ Excel saved: {out_path}")
    print(f"   Sheets: 'All Test Cases' ({len(test_cases)} TCs) + 'Summary'")


# ── Main ────────────────────────────────────────────────────────
if __name__ == "__main__":
    issue_key = sys.argv[1] if len(sys.argv) > 1 else "KAN-5"
    print(f"🔗 Reading .env credentials...")
    env = read_env()
    print(f"   JIRA_URL   : {env.get('JIRA_URL','?')}")
    print(f"   JIRA_TOKEN : {'✅ set' if env.get('JIRA_API_TOKEN') else '❌ missing'}")
    print(f"   GROQ_KEY   : {'✅ set' if env.get('GROQ_KEY') else '❌ missing'}")

    print(f"\n📥 Fetching {issue_key} from Jira...")
    issue = fetch_issue(issue_key, env)
    print(f"   Found: {issue['key']} — {issue['summary']}")

    print(f"\n🤖 Generating comprehensive test cases via GROQ...")
    test_cases = generate_test_cases(issue, env)
    print(f"   Generated: {len(test_cases)} test cases")

    by_type = {}
    for tc in test_cases:
        t = tc.get("type","Unknown")
        by_type[t] = by_type.get(t, 0) + 1
    for t, n in sorted(by_type.items()):
        print(f"   {t:20s}: {n}")

    out_path = os.path.join(_ROOT, f"{issue_key}_Comprehensive_TestCases.xlsx")
    print(f"\n📊 Building Excel...")
    build_excel(issue, test_cases, out_path)

    print(f"\n✅ Done → {out_path}")
