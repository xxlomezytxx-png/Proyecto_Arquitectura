#!/usr/bin/env python3
"""Convert Gitleaks JSON report to standalone HTML."""
import json
import sys
import html
from datetime import datetime

def redact(value: str, keep: int = 4) -> str:
    if not value:
        return ""
    if len(value) <= keep * 2:
        return "*" * len(value)
    return value[:keep] + "*" * (len(value) - keep * 2) + value[-keep:]

def severity_badge(rule_id: str) -> str:
    high_rules = {"generic-api-key", "aws-access-token", "github-pat", "private-key",
                  "password-in-url", "jwt", "twilio", "stripe"}
    sev = "HIGH" if any(r in rule_id.lower() for r in high_rules) else "MEDIUM"
    color = "#e74c3c" if sev == "HIGH" else "#e67e22"
    return f'<span style="background:{color};color:#fff;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:bold">{sev}</span>'

def build_html(findings: list) -> str:
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    total = len(findings)
    high = sum(1 for f in findings if any(r in f.get("RuleID","").lower()
               for r in ["generic-api-key","aws-access-token","github-pat",
                         "private-key","password-in-url","jwt","twilio","stripe"]))
    medium = total - high

    rows = ""
    for f in findings:
        rule = html.escape(f.get("RuleID", ""))
        secret = html.escape(redact(f.get("Secret", "")))
        match = html.escape((f.get("Match", "") or "")[:80])
        file_ = html.escape(f.get("File", ""))
        line = f.get("StartLine", "")
        commit = html.escape((f.get("Commit", "") or "")[:8])
        author = html.escape(f.get("Author", ""))
        date_ = html.escape(f.get("Date", "")[:10] if f.get("Date") else "")
        rows += f"""
        <tr>
          <td>{severity_badge(rule)}</td>
          <td><code>{rule}</code></td>
          <td><code style="color:#e74c3c">{secret}</code></td>
          <td><code>{file_}:{line}</code></td>
          <td><code>{commit}</code></td>
          <td>{author}</td>
          <td>{date_}</td>
        </tr>"""

    no_findings_msg = "" if total else """
    <div style="text-align:center;padding:40px;color:#2ecc71;font-size:1.2em">
      ✅ No secrets detected
    </div>"""

    table_section = f"""
    <table>
      <thead>
        <tr>
          <th>Severity</th><th>Rule ID</th><th>Secret (redacted)</th>
          <th>File:Line</th><th>Commit</th><th>Author</th><th>Date</th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>""" if total else no_findings_msg

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Gitleaks Report — BookFlow</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', sans-serif; background: #0d1117; color: #c9d1d9; padding: 24px; }}
  h1 {{ color: #58a6ff; margin-bottom: 4px; }}
  .meta {{ color: #8b949e; font-size: 13px; margin-bottom: 24px; }}
  .cards {{ display: flex; gap: 16px; margin-bottom: 32px; flex-wrap: wrap; }}
  .card {{ background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 20px 28px; min-width: 140px; }}
  .card .num {{ font-size: 2em; font-weight: bold; }}
  .card .label {{ font-size: 12px; color: #8b949e; margin-top: 4px; }}
  .total .num {{ color: #58a6ff; }}
  .high .num {{ color: #e74c3c; }}
  .medium .num {{ color: #e67e22; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  th {{ background: #161b22; color: #8b949e; text-align: left; padding: 10px 12px; border-bottom: 1px solid #30363d; }}
  td {{ padding: 10px 12px; border-bottom: 1px solid #21262d; vertical-align: top; }}
  tr:hover td {{ background: #161b22; }}
  code {{ font-family: 'Consolas', monospace; font-size: 12px; word-break: break-all; }}
  h2 {{ color: #c9d1d9; margin-bottom: 16px; font-size: 1em; text-transform: uppercase; letter-spacing: 1px; }}
</style>
</head>
<body>
<h1>🔑 Gitleaks — Secret Detection Report</h1>
<p class="meta">BookFlow AI Commerce · Generated {now}</p>
<div class="cards">
  <div class="card total"><div class="num">{total}</div><div class="label">Total Findings</div></div>
  <div class="card high"><div class="num">{high}</div><div class="label">High Severity</div></div>
  <div class="card medium"><div class="num">{medium}</div><div class="label">Medium Severity</div></div>
</div>
<h2>Findings</h2>
{table_section}
</body>
</html>"""

def main():
    input_file = sys.argv[1] if len(sys.argv) > 1 else "reports/gitleaks.json"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "reports/gitleaks.html"
    try:
        with open(input_file) as f:
            data = json.load(f)
        findings = data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        findings = []
    with open(output_file, "w") as f:
        f.write(build_html(findings))
    print(f"Gitleaks HTML report → {output_file} ({len(findings)} findings)")

if __name__ == "__main__":
    main()
