"""
Layer 3 Tool: Generate KAN-5 test cases in exact table format from the screenshot.
Columns: Test_Case | TaxPlanCode | Plan Booster Entity | Employer Plan Key | Expected Result
"""
import os, sys, json, base64, re
import requests
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from groq import Groq

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ── 1. Read .env ─────────────────────────────────────────────────
def read_env():
    env = {}
    with open(os.path.join(_ROOT, ".env"), encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and "=" in line and not line.startswith("#"):
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip()
    return env


# ── 2. Fetch Jira Issue ──────────────────────────────────────────
def fetch_issue(issue_key, env):
    url  = f"{env['JIRA_URL'].rstrip('/')}/rest/api/3/issue/{issue_key}"
    cred = base64.b64encode(
        f"{env['JIRA_EMAIL']}:{env['JIRA_API_TOKEN']}".encode()
    ).decode()
    resp = requests.get(
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
    }


# ── 3. GROQ: Generate test cases in the exact 5-column format ───
PROMPT = """You are a senior QA engineer for a financial tax system.

Jira Issue: {key}
Summary: {summary}
Description:
{description}

The business rule is:
- TaxPlanCode must be 1247Q
- Plan Booster Entity must NOT be: PRVCX, PRVQX, PRVZX, PRVTX
- Employer Plan Key must NOT be: 721450-X2, 721451-X2, 884203-X2, 664912-X2
- If ALL conditions are met → "New C12.0- Green text and Light Black text should print -IN"
- If ANY condition fails → "New C12.0- Green text and Light Black text should not print -OUT"

Generate ALL meaningful test cases in this EXACT JSON format (pure JSON, no markdown):

{{
  "test_cases": [
    {{
      "Test_Case": "Test_01",
      "TaxPlanCode": "1247Q",
      "Plan_Booster_Entity": "NOT PRVCX and\\nNOT PRVQX and\\nNOT PRVZX and\\nNOT PRVTX",
      "Employer_Plan_Key": "NOT 721450-X2\\nNOT 721451-X2\\nNOT 884203-X2\\nNOT 664912-X2",
      "Expected_Result": "New C12.0- Green text and Light Black text should print -IN",
      "Outcome": "IN"
    }}
  ]
}}

REQUIRED test cases (generate ALL of these):

POSITIVE (Outcome=IN):
1. All entities valid (NOT any of the 4 excluded) + all plan keys valid (NOT any of the 4 excluded) + TaxPlanCode=1247Q
2. Single valid entity (e.g. PRVAX) + single valid plan key (e.g. 123456-X1) + TaxPlanCode=1247Q
3. Multiple valid entities + single valid plan key + TaxPlanCode=1247Q

NEGATIVE (Outcome=OUT) - one test case for EACH excluded value:
4.  PRVCX + valid plan key + TaxPlanCode=1247Q → OUT
5.  PRVQX + valid plan key + TaxPlanCode=1247Q → OUT
6.  PRVZX + valid plan key + TaxPlanCode=1247Q → OUT
7.  PRVTX + valid plan key + TaxPlanCode=1247Q → OUT
8.  Valid entity + 721450-X2 + TaxPlanCode=1247Q → OUT
9.  Valid entity + 721451-X2 + TaxPlanCode=1247Q → OUT
10. Valid entity + 884203-X2 + TaxPlanCode=1247Q → OUT
11. Valid entity + 664912-X2 + TaxPlanCode=1247Q → OUT
12. Wrong TaxPlanCode (e.g. 9999X) + valid entity + valid plan key → OUT
13. PRVCX + 721450-X2 (both excluded) + TaxPlanCode=1247Q → OUT
14. All 4 excluded entities + all 4 excluded plan keys → OUT

EDGE CASES (Outcome=OUT or IN as logic dictates):
15. Empty TaxPlanCode → OUT
16. TaxPlanCode=1247q (lowercase) → OUT
17. Valid entity + valid plan key but TaxPlanCode has trailing space → OUT
18. Null/missing Plan Booster Entity → OUT

Number each test case sequentially: Test_01, Test_02, Test_03... etc.
Return ONLY valid JSON."""


def generate_test_cases(issue, env):
    client = Groq(api_key=env["GROQ_KEY"])
    resp   = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": PROMPT.format(**issue)}],
        temperature=0.1,
        max_tokens=6000,
    )
    raw = resp.choices[0].message.content.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw.rstrip())
    data = json.loads(raw)
    return data["test_cases"]


# ── 4. Build Excel in exact screenshot format ────────────────────
THIN   = Side(style="thin",   color="000000")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

HEADER_FILL = PatternFill("solid", fgColor="FFFFFF")
HEADER_FONT = Font(name="Calibri", bold=True, size=11, color="000000")
BODY_FONT   = Font(name="Calibri", size=10, color="000000")

CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
LEFT   = Alignment(horizontal="left",   vertical="center", wrap_text=True)


def build_excel(issue, test_cases, out_path):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "KAN-5 Test Cases"

    # ── Column definitions (matches screenshot exactly) ──────────
    COLS = [
        ("Test_Case",          14),
        ("TaxPlanCode",        14),
        ("Plan Booster Entity",30),
        ("Employer Plan Key",  30),
        ("Expected Result",    50),
    ]

    # ── Title banner ─────────────────────────────────────────────
    ws.merge_cells(f"A1:{get_column_letter(len(COLS))}1")
    t          = ws["A1"]
    t.value    = f"{issue['key']}  —  {issue['summary']}"
    t.font     = Font(name="Calibri", bold=True, size=12, color="FFFFFF")
    t.fill     = PatternFill("solid", fgColor="0052CC")
    t.alignment= CENTER
    ws.row_dimensions[1].height = 26

    # ── Header row (bold, white bg, black text, bordered) ────────
    for ci, (label, width) in enumerate(COLS, start=1):
        c = ws.cell(row=2, column=ci, value=label)
        c.font      = HEADER_FONT
        c.fill      = HEADER_FILL
        c.alignment = CENTER
        c.border    = BORDER
        ws.column_dimensions[get_column_letter(ci)].width = width
    ws.row_dimensions[2].height = 22

    # ── Data rows ─────────────────────────────────────────────────
    for ri, tc in enumerate(test_cases, start=3):
        outcome = tc.get("Outcome", "").upper()
        # Light fill: green for IN, salmon for OUT, white for edge
        if outcome == "IN":
            row_fill = PatternFill("solid", fgColor="E2EFDA")
        elif outcome == "OUT":
            row_fill = PatternFill("solid", fgColor="FCE4D6")
        else:
            row_fill = PatternFill("solid", fgColor="FFFFFF")

        def safe(val):
            return (val or "").replace("\\n", "\n")

        values = [
            tc.get("Test_Case", ""),
            tc.get("TaxPlanCode", ""),
            safe(tc.get("Plan_Booster_Entity")),
            safe(tc.get("Employer_Plan_Key")),
            tc.get("Expected_Result", "") or "",
        ]

        for ci, val in enumerate(values, start=1):
            c = ws.cell(row=ri, column=ci, value=val)
            c.font      = Font(name="Calibri", size=10, bold=(ci == 1))
            c.fill      = row_fill
            c.border    = BORDER
            c.alignment = CENTER if ci <= 2 else LEFT

        # Auto row height based on newlines in entity/plan key columns
        lines = max(
            len(str(values[2]).split("\n")),
            len(str(values[3]).split("\n")),
            2
        )
        ws.row_dimensions[ri].height = max(40, lines * 18)

    ws.freeze_panes = "A3"

    wb.save(out_path)
    print(f"✅ Saved: {out_path}  ({len(test_cases)} test cases)")


# ── Main ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    issue_key = sys.argv[1] if len(sys.argv) > 1 else "KAN-5"

    print("🔗 Reading .env...")
    env = read_env()
    print(f"   JIRA_URL  : {env.get('JIRA_URL')}")
    print(f"   JIRA_TOKEN: {'✅' if env.get('JIRA_API_TOKEN') else '❌'}")
    print(f"   GROQ_KEY  : {'✅' if env.get('GROQ_KEY') else '❌'}")

    print(f"\n📥 Fetching {issue_key} from Jira...")
    issue = fetch_issue(issue_key, env)
    print(f"   {issue['key']} — {issue['summary']}")

    print("\n🤖 Generating test cases via GROQ...")
    test_cases = generate_test_cases(issue, env)

    from collections import Counter
    counts = Counter(tc.get("Outcome","?") for tc in test_cases)
    print(f"   Total: {len(test_cases)}  |  IN: {counts['IN']}  |  OUT: {counts['OUT']}")

    out_path = os.path.join(_ROOT, f"{issue_key}_TestCases.xlsx")
    print(f"\n📊 Building Excel → {out_path}")
    build_excel(issue, test_cases, out_path)
    print("\n✅ Done — open with Microsoft Excel")
