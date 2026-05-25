#!/usr/bin/env python3
"""Convert Semgrep JSON report to standalone HTML."""
import json
import sys
import html
from datetime import datetime
from collections import Counter

SEV_ORDER = {"ERROR": 0, "WARNING": 1, "INFO": 2}
SEV_COLOR = {"ERROR": "#e74c3c", "WARNING": "#e67e22", "INFO": "#3498db"}
SEV_LABEL = {"ERROR": "HIGH", "WARNING": "MEDIUM", "INFO": "LOW"}

def build_html(results: list, errors: list) -> str:
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    total = len(results)
    counts = Counter(r.get("extra", {}).get("severity", "INFO").upper() for r in results)

    rows = ""
    for r in sorted(results, key=lambda x: SEV_ORDER.get(
            x.get("extra", {}).get("severity", "INFO").upper(), 99)):
        sev_raw = r.get("extra", {}).get("severity", "INFO").upper()
        color = SEV_COLOR.get(sev_raw, "#8b949e")
        label = SEV_LABEL.get(sev_raw, sev_raw)
        badge = f'<span style="background:{color};color:#fff;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:bold">{label}</span>'

        path = html.escape(r.get("path", ""))
        start = r.get("start", {})
        line = start.get("line", "")
        rule_id = html.escape(r.get("check_id", ""))
        message = html.escape((r.get("extra", {}).get("message", "") or "")[:200])
        snippet = html.escape((r.get("extra", {}).get("lines", "") or "").strip()[:120])

        rows += f"""
        <tr>
          <td>{badge}</td>
          <td><code style="font-size:11px">{rule_id}</code></td>
          <td><code>{path}:{line}</code></td>
          <td>{message}</td>
          <td><code style="color:#8b949e">{snippet}</code></td>
        </tr>"""

    error_rows = ""
    for e in errors[:10]:
        msg = html.escape(str(e.get("message", e))[:200])
        error_rows += f"<li><code>{msg}</code></li>"

    error_section = f"""
    <h2 style="margin-top:32px">Scan Errors ({len(errors)})</h2>
    <ul style="color:#e74c3c;font-size:13px;margin-left:20px">{error_rows}</ul>""" if errors else ""

    no_findings_msg = "" if total else """
    <div style="text-align:center;padding:40px;color:#2ecc71;font-size:1.2em">
      ✅ No findings detected
    </div>"""

    table_section = f"""
    <table>
      <thead>
        <tr>
          <th>Severity</th><th>Rule ID</th><th>Location</th><th>Message</th><th>Code</th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>""" if total else no_findings_msg

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Semgrep Report — BookFlow</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', sans-serif; background: #0d1117; color: #c9d1d9; padding: 24px; }}
  h1 {{ color: #58a6ff; margin-bottom: 4px; }}
  .meta {{ color: #8b949e; font-size: 13px; margin-bottom: 24px; }}
  .cards {{ display: flex; gap: 16px; margin-bottom: 32px; flex-wrap: wrap; }}
  .card {{ background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 20px 28px; min-width: 140px; }}
  .card .num {{ font-size: 2em; font-weight: bold; }}
  .card .label {{ font-size: 12px; color: #8b949e; margin-top: 4px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  th {{ background: #161b22; color: #8b949e; text-align: left; padding: 10px 12px; border-bottom: 1px solid #30363d; }}
  td {{ padding: 10px 12px; border-bottom: 1px solid #21262d; vertical-align: top; max-width: 300px; word-break: break-word; }}
  tr:hover td {{ background: #161b22; }}
  code {{ font-family: 'Consolas', monospace; font-size: 12px; word-break: break-all; }}
  h2 {{ color: #c9d1d9; margin-bottom: 16px; font-size: 1em; text-transform: uppercase; letter-spacing: 1px; }}
</style>
</head>
<body>
<h1>🔍 Semgrep — SAST Report</h1>
<p class="meta">BookFlow AI Commerce · Generated {now}</p>
<div class="cards">
  <div class="card" style="border-color:#58a6ff">
    <div class="num" style="color:#58a6ff">{total}</div>
    <div class="label">Total Findings</div>
  </div>
  <div class="card" style="border-color:#e74c3c">
    <div class="num" style="color:#e74c3c">{counts.get('ERROR', 0)}</div>
    <div class="label">High (ERROR)</div>
  </div>
  <div class="card" style="border-color:#e67e22">
    <div class="num" style="color:#e67e22">{counts.get('WARNING', 0)}</div>
    <div class="label">Medium (WARNING)</div>
  </div>
  <div class="card" style="border-color:#3498db">
    <div class="num" style="color:#3498db">{counts.get('INFO', 0)}</div>
    <div class="label">Low (INFO)</div>
  </div>
</div>
<h2>Findings</h2>
{table_section}
{error_section}
</body>
</html>"""

def main():
    input_file = sys.argv[1] if len(sys.argv) > 1 else "reports/semgrep.json"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "reports/semgrep.html"
    try:
        with open(input_file) as f:
            data = json.load(f)
        results = data.get("results", [])
        errors = data.get("errors", [])
    except (FileNotFoundError, json.JSONDecodeError):
        results, errors = [], []
    with open(output_file, "w") as f:
        f.write(build_html(results, errors))
    print(f"Semgrep HTML report → {output_file} ({len(results)} findings)")

if __name__ == "__main__":
    main()
