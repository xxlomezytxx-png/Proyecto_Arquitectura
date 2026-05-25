#!/usr/bin/env python3
"""Convert Checkov JSON report to standalone HTML."""
import json
import sys
import html
from datetime import datetime
from collections import defaultdict

SEV_COLOR = {"HIGH": "#e74c3c", "MEDIUM": "#e67e22", "LOW": "#3498db", "UNKNOWN": "#8b949e"}

def load_checks(path: str):
    try:
        with open(path) as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return [], [], []

    # checkov can return a list (multi-framework) or a single dict
    entries = data if isinstance(data, list) else [data]

    passed, failed, errors = [], [], []
    for block in entries:
        if not isinstance(block, dict):
            continue
        passed.extend(block.get("passed", []) or [])
        failed.extend(block.get("failed", []) or [])
        errors.extend(block.get("parsing_errors", []) or [])
    return passed, failed, errors

def sev_badge(check_id: str) -> str:
    cid = check_id.upper()
    if any(k in cid for k in ["SECRET", "PASSWORD", "CRED", "AUTH", "PRIV"]):
        sev, color = "HIGH", SEV_COLOR["HIGH"]
    elif any(k in cid for k in ["EXPOSE", "ROOT", "SUDO", "NETWORK", "PORT"]):
        sev, color = "MEDIUM", SEV_COLOR["MEDIUM"]
    else:
        sev, color = "LOW", SEV_COLOR["LOW"]
    return f'<span style="background:{color};color:#fff;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:bold">{sev}</span>', sev

def build_html(passed: list, failed: list, errors: list) -> str:
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    total_pass = len(passed)
    total_fail = len(failed)
    total = total_pass + total_fail

    sev_counts = defaultdict(int)
    rows = ""
    for f in failed:
        check_id = f.get("check_id", "")
        check_name = f.get("check_name", "")
        file_path = f.get("file_path", f.get("repo_file_path", ""))
        line_range = f.get("file_line_range", [])
        resource = f.get("resource", "")

        badge, sev = sev_badge(check_id)
        sev_counts[sev] += 1
        line_info = f"{line_range[0]}–{line_range[1]}" if len(line_range) == 2 else ""

        rows += f"""
        <tr>
          <td>{badge}</td>
          <td><code style="font-size:11px">{html.escape(check_id)}</code></td>
          <td>{html.escape(check_name)}</td>
          <td><code>{html.escape(file_path)}:{line_info}</code></td>
          <td><code style="color:#8b949e">{html.escape(resource)}</code></td>
        </tr>"""

    error_items = "".join(
        f"<li><code>{html.escape(str(e)[:200])}</code></li>" for e in errors[:10]
    )
    error_section = f"""
    <h2 style="margin-top:32px">Parsing Errors ({len(errors)})</h2>
    <ul style="color:#e74c3c;font-size:13px;margin-left:20px">{error_items}</ul>""" if errors else ""

    no_failures = "" if total_fail else """
    <div style="text-align:center;padding:40px;color:#2ecc71;font-size:1.2em">
      ✅ No IaC issues detected
    </div>"""

    table_section = f"""
    <table>
      <thead>
        <tr>
          <th>Severity</th><th>Check ID</th><th>Check Name</th>
          <th>File:Lines</th><th>Resource</th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>""" if total_fail else no_failures

    pass_rate = int(total_pass / total * 100) if total else 100
    bar_color = "#2ecc71" if pass_rate >= 80 else "#e67e22" if pass_rate >= 50 else "#e74c3c"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Checkov IaC Report — BookFlow</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', sans-serif; background: #0d1117; color: #c9d1d9; padding: 24px; }}
  h1 {{ color: #58a6ff; margin-bottom: 4px; }}
  .meta {{ color: #8b949e; font-size: 13px; margin-bottom: 24px; }}
  .cards {{ display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; }}
  .card {{ background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 20px 28px; min-width: 140px; }}
  .card .num {{ font-size: 2em; font-weight: bold; }}
  .card .label {{ font-size: 12px; color: #8b949e; margin-top: 4px; }}
  .progress-wrap {{ background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 16px 24px; margin-bottom: 32px; }}
  .bar-bg {{ background: #21262d; border-radius: 4px; height: 12px; overflow: hidden; margin-top: 8px; }}
  .bar-fill {{ height: 100%; border-radius: 4px; transition: width 0.3s; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  th {{ background: #161b22; color: #8b949e; text-align: left; padding: 10px 12px; border-bottom: 1px solid #30363d; }}
  td {{ padding: 10px 12px; border-bottom: 1px solid #21262d; vertical-align: top; max-width: 280px; word-break: break-word; }}
  tr:hover td {{ background: #161b22; }}
  code {{ font-family: 'Consolas', monospace; font-size: 12px; word-break: break-all; }}
  h2 {{ color: #c9d1d9; margin-bottom: 16px; font-size: 1em; text-transform: uppercase; letter-spacing: 1px; }}
</style>
</head>
<body>
<h1>🛡️ Checkov — IaC Security Report</h1>
<p class="meta">BookFlow AI Commerce · Generated {now}</p>
<div class="cards">
  <div class="card" style="border-color:#58a6ff">
    <div class="num" style="color:#58a6ff">{total}</div>
    <div class="label">Checks Run</div>
  </div>
  <div class="card" style="border-color:#2ecc71">
    <div class="num" style="color:#2ecc71">{total_pass}</div>
    <div class="label">Passed</div>
  </div>
  <div class="card" style="border-color:#e74c3c">
    <div class="num" style="color:#e74c3c">{total_fail}</div>
    <div class="label">Failed</div>
  </div>
  <div class="card" style="border-color:#e74c3c">
    <div class="num" style="color:#e74c3c">{sev_counts.get('HIGH', 0)}</div>
    <div class="label">High</div>
  </div>
  <div class="card" style="border-color:#e67e22">
    <div class="num" style="color:#e67e22">{sev_counts.get('MEDIUM', 0)}</div>
    <div class="label">Medium</div>
  </div>
</div>
<div class="progress-wrap">
  <span style="font-size:13px;color:#8b949e">Pass rate: <strong style="color:{bar_color}">{pass_rate}%</strong></span>
  <div class="bar-bg"><div class="bar-fill" style="width:{pass_rate}%;background:{bar_color}"></div></div>
</div>
<h2>Failed Checks</h2>
{table_section}
{error_section}
</body>
</html>"""

def main():
    input_file = sys.argv[1] if len(sys.argv) > 1 else "reports/checkov.json"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "reports/checkov.html"
    passed, failed, errors = load_checks(input_file)
    with open(output_file, "w") as f:
        f.write(build_html(passed, failed, errors))
    print(f"Checkov HTML report → {output_file} ({len(failed)} failures / {len(passed)} passed)")

if __name__ == "__main__":
    main()
