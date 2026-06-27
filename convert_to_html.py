import sys
sys.path.insert(0, r"c:\AI\3x\Chatpter_3_BLAST_FramWork\Lib\site-packages")
import markdown, pathlib

md_text = pathlib.Path(r"c:\AI\3x\Chatpter_3_BLAST_FramWork\test_plan_output.md").read_text(encoding="utf-8")
body = markdown.markdown(md_text, extensions=["tables"])

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Test Plan: KAN-1 — User Login Functionality</title>
<style>
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    max-width: 860px; margin: 40px auto; padding: 0 24px;
    color: #222; line-height: 1.7;
  }}
  h1 {{ color: #0052cc; border-bottom: 3px solid #0052cc; padding-bottom: 8px; }}
  h3 {{ color: #0065ff; margin-top: 2em; }}
  h4 {{ color: #333; }}
  table {{ border-collapse: collapse; width: 100%; margin: 1em 0; }}
  th {{ background: #0052cc; color: #fff; padding: 10px 14px; text-align: left; }}
  td {{ padding: 9px 14px; border: 1px solid #ddd; }}
  tr:nth-child(even) td {{ background: #f4f7ff; }}
  code {{ background: #f0f0f0; padding: 2px 6px; border-radius: 4px; font-size: 0.9em; }}
  ul, ol {{ padding-left: 1.5em; }}
  li {{ margin-bottom: 4px; }}
  .badge {{
    display: inline-block; background: #0052cc; color: #fff;
    padding: 2px 12px; border-radius: 12px; font-size: 0.85em; margin-bottom: 1em;
  }}
</style>
</head>
<body>
<span class="badge">Jira &bull; KAN-1</span>
{body}
</body>
</html>"""

out = r"c:\AI\3x\Chatpter_3_BLAST_FramWork\test_plan_output.html"
pathlib.Path(out).write_text(html, encoding="utf-8")
print("HTML written to", out)
