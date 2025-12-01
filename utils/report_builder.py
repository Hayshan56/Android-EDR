#!/usr/bin/env python3
"""
utils/report_builder.py
Creates human-readable reports from scan results.
Outputs: .txt, .json, .html
"""
import json
from pathlib import Path
import time

REPORTS = Path("reports")
REPORTS.mkdir(exist_ok=True)

def _write(path, data):
    try:
        path.write_text(data)
    except Exception:
        pass

def generate_json(result, name=None):
    ts = int(time.time())
    fname = name or f"report_{ts}.json"
    path = REPORTS / fname
    _write(path, json.dumps(result, indent=2))
    return str(path)

def generate_text(result, name=None):
    ts = int(time.time())
    fname = name or f"report_{ts}.txt"
    path = REPORTS / fname

    out = []
    out.append("=== ANDROID-EDR SCAN REPORT ===")
    out.append(f"Timestamp: {ts}")
    out.append("")

    for k, v in result.items():
        out.append(f"[{k.upper()}]")
        out.append(json.dumps(v, indent=2))
        out.append("")

    _write(path, "\n".join(out))
    return str(path)

def generate_html(result, name=None):
    ts = int(time.time())
    fname = name or f"report_{ts}.html"
    path = REPORTS / fname

    html = [
        "<html><head><title>Android EDR Report</title>",
        "<style>body{font-family:Arial;}pre{background:#eee;padding:10px;border-radius:6px;}</style>",
        "</head><body>",
        "<h1>Android EDR Scan Report</h1>",
        f"<p>Generated: {ts}</p>"
    ]

    for k, v in result.items():
        html.append(f"<h2>{k.upper()}</h2>")
        html.append("<pre>")
        html.append(json.dumps(v, indent=2))
        html.append("</pre>")

    html.append("</body></html>")

    _write(path, "\n".join(html))
    return str(path)
