#!/usr/bin/env python3
"""
core/dashboard.py

Mobile-first, Tailwind CSS premium dashboard (single-file).
Serves a single-page app and a tiny JSON API for reports.

Usage:
  python3 core/dashboard.py
Or copy to prefix and run via launcher.

Endpoints:
  GET  /               -> SPA
  GET  /api/reports    -> list of report summaries
  GET  /api/report/<ts>-> return report JSON
  GET  /api/report/<ts>/html -> download formatted HTML report
  GET  /api/report/<ts>/text -> download formatted text report
  DELETE /api/report/<ts> -> delete report
  GET  /api/user       -> { "name": "<username or null>" }
  POST /api/setname    -> { "name": "..." }  (JSON or form)
"""
import http.server
import socketserver
import json
import os
import urllib.parse
from pathlib import Path
import io
import sys
import time
from datetime import datetime
import base64

HOME = Path.home()
REPORT_DIR = HOME / "Android-EDR-Reports"
USER_FILE = HOME / ".aedr_user"
HOST = "127.0.0.1"
PORT = 8080

# Ensure report dir exists
def ensure_report_dir():
    try:
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

def get_username():
    try:
        txt = USER_FILE.read_text(encoding="utf-8").strip()
        return txt if txt else None
    except Exception:
        return None

def set_username(name):
    try:
        USER_FILE.write_text(name.strip(), encoding="utf-8")
        return True
    except Exception:
        return False

def list_reports():
    ensure_report_dir()
    files = sorted(REPORT_DIR.glob("report_*.json"), reverse=True)
    out = []
    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            # Use timestamp from file content if available, otherwise parse from filename
            ts = data.get("timestamp") or int(f.stem.replace("report_", ""))

            # Determine the highest severity for the report summary
            findings = data.get("findings", [])
            severities = [item.get("severity", "low").lower() for item in findings]

            # Map severity to an orderable rank (critical > high > medium > low)
            rank = {"critical": 4, "high": 3, "medium": 2, "low": 1, "default": 0}
            highest_rank = max([rank.get(s, 0) for s in severities], default=0)
            highest_severity = next((k for k, v in rank.items() if v == highest_rank), "low")

            out.append({
                "ts": ts,
                "summary_count": len(findings),
                "path": f.name,
                "highest_severity": highest_severity # Add for UI
            })
        except Exception:
            continue
    return out

def read_report(ts):
    fname = REPORT_DIR / f"report_{ts}.json"
    if not fname.exists():
        return None
    try:
        data = json.loads(fname.read_text(encoding="utf-8"))
        # Ensure timestamp is in the data for client-side use
        if "timestamp" not in data:
             data["timestamp"] = int(ts)
        return data
    except Exception:
        return None

def delete_report(ts):
    fname = REPORT_DIR / f"report_{ts}.json"
    try:
        if fname.exists():
            fname.unlink()
            return True
    except Exception:
        pass
    return False

def generate_html_report(data):
    """Generate a professional HTML report from JSON data"""
    ts = data.get("timestamp", "unknown")
    dt = datetime.fromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M:%S")
    
    findings = data.get("findings", [])
    events = data.get("events", [])
    device_info = data.get("device_info", {})
    
    # Count severities
    severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for f in findings:
        sev = f.get("severity", "low").lower()
        severity_counts[sev] = severity_counts.get(sev, 0) + 1
    
    # Generate severity badges HTML
    def get_severity_badge(severity):
        severity = severity.lower()
        if severity == "critical":
            return '<span class="badge critical">CRITICAL</span>'
        elif severity == "high":
            return '<span class="badge high">HIGH</span>'
        elif severity == "medium":
            return '<span class="badge medium">MEDIUM</span>'
        else:
            return '<span class="badge low">LOW</span>'
    
    # Generate findings HTML
    findings_html = ""
    for i, finding in enumerate(findings, 1):
        severity = finding.get("severity", "low").lower()
        findings_html += f"""
        <div class="finding">
            <h3>Finding #{i}: {finding.get('title', 'No title')} {get_severity_badge(severity)}</h3>
            <div class="finding-details">
                <div class="detail-row">
                    <span class="detail-label">Type:</span>
                    <span class="detail-value">{finding.get('type', 'Unknown')}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Module:</span>
                    <span class="detail-value">{finding.get('module', 'N/A')}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Rule:</span>
                    <span class="detail-value">{finding.get('rule', 'N/A')}</span>
                </div>
        """
        
        if finding.get('path'):
            findings_html += f"""
                <div class="detail-row">
                    <span class="detail-label">Path:</span>
                    <span class="detail-value">{finding.get('path')}</span>
                </div>
            """
            if finding.get('line'):
                findings_html += f"""
                    <div class="detail-row">
                        <span class="detail-label">Line:</span>
                        <span class="detail-value">{finding.get('line')}</span>
                    </div>
                """
        
        if finding.get('summary'):
            findings_html += f"""
                <div class="detail-row full-width">
                    <span class="detail-label">Summary:</span>
                    <span class="detail-value">{finding.get('summary')}</span>
                </div>
            """
        
        if finding.get('detail'):
            detail_text = str(finding.get('detail')).replace('\n', '<br>')
            findings_html += f"""
                <div class="detail-row full-width">
                    <span class="detail-label">Evidence:</span>
                    <div class="detail-value evidence">
                        <pre>{detail_text}</pre>
                    </div>
                </div>
            """
        
        findings_html += """
            </div>
        </div>
        """
    
    # Generate device info HTML
    device_info_html = ""
    if device_info:
        device_info_html = "<h3>Device Information</h3><table>"
        for key, value in device_info.items():
            if value:
                formatted_key = key.replace('_', ' ').title()
                device_info_html += f"""
                <tr>
                    <td><strong>{formatted_key}</strong></td>
                    <td>{value}</td>
                </tr>
                """
        device_info_html += "</table>"
    
    # Generate events HTML
    events_html = ""
    if events:
        events_html = "<h3>Recent Events (Last 50)</h3><table>"
        events_html += "<tr><th>#</th><th>Time</th><th>Type</th><th>Details</th></tr>"
        for i, event in enumerate(events[:50], 1):
            event_type = event.get('type', 'Unknown')
            event_time = event.get('timestamp', '')
            if event_time:
                try:
                    event_time = datetime.fromtimestamp(int(event_time)).strftime("%H:%M:%S")
                except:
                    event_time = str(event_time)
            
            event_data = event.get('data', {})
            data_str = str(event_data)
            if len(data_str) > 100:
                data_str = data_str[:97] + "..."
            
            events_html += f"""
            <tr>
                <td>{i}</td>
                <td>{event_time}</td>
                <td>{event_type}</td>
                <td>{data_str}</td>
            </tr>
            """
        events_html += "</table>"
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Android-EDR Security Report</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f8fafc;
            padding: 20px;
        }}
        
        .report-container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #007AFF 0%, #0056CC 100%);
            color: white;
            padding: 30px 40px;
        }}
        
        .header h1 {{
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 10px;
        }}
        
        .header .subtitle {{
            font-size: 16px;
            opacity: 0.9;
            margin-bottom: 20px;
        }}
        
        .header-meta {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-top: 20px;
        }}
        
        .meta-item {{
            background: rgba(255, 255, 255, 0.1);
            padding: 12px 20px;
            border-radius: 8px;
            backdrop-filter: blur(10px);
        }}
        
        .meta-item .label {{
            font-size: 12px;
            opacity: 0.8;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .meta-item .value {{
            font-size: 16px;
            font-weight: 600;
            margin-top: 4px;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .summary-card {{
            background: #f8fafc;
            padding: 24px;
            border-radius: 10px;
            text-align: center;
            border: 1px solid #e2e8f0;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .summary-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        }}
        
        .summary-card.critical {{ border-left: 4px solid #E53E3E; }}
        .summary-card.high {{ border-left: 4px solid #DD6B20; }}
        .summary-card.medium {{ border-left: 4px solid #D69E2E; }}
        .summary-card.low {{ border-left: 4px solid #38A169; }}
        
        .summary-card .count {{
            font-size: 36px;
            font-weight: 700;
            margin-bottom: 8px;
        }}
        
        .summary-card.critical .count {{ color: #E53E3E; }}
        .summary-card.high .count {{ color: #DD6B20; }}
        .summary-card.medium .count {{ color: #D69E2E; }}
        .summary-card.low .count {{ color: #38A169; }}
        
        .summary-card .label {{
            font-size: 14px;
            color: #4a5568;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        section {{
            margin-bottom: 40px;
        }}
        
        section h2 {{
            font-size: 24px;
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e2e8f0;
        }}
        
        .finding {{
            background: #f8fafc;
            border-radius: 10px;
            padding: 24px;
            margin-bottom: 20px;
            border: 1px solid #e2e8f0;
            transition: transform 0.2s;
        }}
        
        .finding:hover {{
            transform: translateX(5px);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }}
        
        .finding h3 {{
            font-size: 18px;
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        
        .finding-details {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 12px;
        }}
        
        .detail-row {{
            display: flex;
            align-items: flex-start;
        }}
        
        .detail-row.full-width {{
            grid-column: 1 / -1;
        }}
        
        .detail-label {{
            font-weight: 600;
            color: #4a5568;
            min-width: 100px;
            margin-right: 12px;
            font-size: 14px;
        }}
        
        .detail-value {{
            flex: 1;
            color: #2d3748;
            font-size: 14px;
            word-break: break-word;
        }}
        
        .detail-value.evidence {{
            background: #edf2f7;
            padding: 12px;
            border-radius: 6px;
            border: 1px solid #cbd5e0;
        }}
        
        .detail-value.evidence pre {{
            white-space: pre-wrap;
            word-wrap: break-word;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 12px;
            line-height: 1.4;
            margin: 0;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        }}
        
        table th {{
            background: #f8fafc;
            padding: 16px;
            text-align: left;
            font-weight: 600;
            color: #4a5568;
            border-bottom: 2px solid #e2e8f0;
            font-size: 14px;
        }}
        
        table td {{
            padding: 14px 16px;
            border-bottom: 1px solid #e2e8f0;
            font-size: 14px;
        }}
        
        table tr:last-child td {{
            border-bottom: none;
        }}
        
        table tr:hover td {{
            background: #f8fafc;
        }}
        
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .badge.critical {{
            background: #FED7D7;
            color: #9B2C2C;
        }}
        
        .badge.high {{
            background: #FEEBC8;
            color: #9C4221;
        }}
        
        .badge.medium {{
            background: #FAF089;
            color: #744210;
        }}
        
        .badge.low {{
            background: #C6F6D5;
            color: #276749;
        }}
        
        .watermark {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e2e8f0;
            color: #a0aec0;
            font-size: 14px;
        }}
        
        .watermark strong {{
            color: #007AFF;
        }}
        
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            
            .report-container {{
                box-shadow: none;
                border-radius: 0;
            }}
            
            .header {{
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
            }}
            
            .summary-card {{
                page-break-inside: avoid;
            }}
            
            .finding {{
                page-break-inside: avoid;
            }}
            
            table {{
                page-break-inside: avoid;
            }}
        }}
        
        @media (max-width: 768px) {{
            .content {{
                padding: 20px;
            }}
            
            .header {{
                padding: 20px;
            }}
            
            .header h1 {{
                font-size: 24px;
            }}
            
            .summary-cards {{
                grid-template-columns: repeat(2, 1fr);
            }}
            
            .finding-details {{
                grid-template-columns: 1fr;
            }}
            
            .detail-row {{
                flex-direction: column;
                gap: 4px;
            }}
            
            .detail-label {{
                min-width: auto;
            }}
            
            table {{
                display: block;
                overflow-x: auto;
            }}
        }}
    </style>
</head>
<body>
    <div class="report-container">
        <div class="header">
            <h1>Android-EDR Security Report</h1>
            <div class="subtitle">Enterprise Detection & Response</div>
            <div class="header-meta">
                <div class="meta-item">
                    <div class="label">Report ID</div>
                    <div class="value">#{ts}</div>
                </div>
                <div class="meta-item">
                    <div class="label">Generated</div>
                    <div class="value">{dt}</div>
                </div>
                <div class="meta-item">
                    <div class="label">Total Findings</div>
                    <div class="value">{len(findings)}</div>
                </div>
                <div class="meta-item">
                    <div class="label">Total Events</div>
                    <div class="value">{len(events)}</div>
                </div>
            </div>
        </div>
        
        <div class="content">
            <section>
                <h2>Executive Summary</h2>
                <div class="summary-cards">
                    <div class="summary-card critical">
                        <div class="count">{severity_counts['critical']}</div>
                        <div class="label">Critical</div>
                    </div>
                    <div class="summary-card high">
                        <div class="count">{severity_counts['high']}</div>
                        <div class="label">High</div>
                    </div>
                    <div class="summary-card medium">
                        <div class="count">{severity_counts['medium']}</div>
                        <div class="label">Medium</div>
                    </div>
                    <div class="summary-card low">
                        <div class="count">{severity_counts['low']}</div>
                        <div class="label">Low</div>
                    </div>
                </div>
            </section>
            
            {device_info_html}
            
            <section>
                <h2>Security Findings</h2>
                {findings_html if findings else '<p class="no-findings">No security findings detected. Device appears clean.</p>'}
            </section>
            
            {events_html}
            
            <div class="watermark">
                <p>Generated by <strong>Android-EDR</strong> | Made by <strong>HAYSHAN</strong></p>
                <p style="font-size: 12px; margin-top: 8px; opacity: 0.8;">Report automatically generated by Android Enterprise Detection & Response System</p>
            </div>
        </div>
    </div>
    
    <script>
        // Add print functionality
        document.addEventListener('DOMContentLoaded', function() {{
            // Auto-print when opened (optional)
            // setTimeout(() => window.print(), 1000);
            
            // Add print button for convenience
            const printBtn = document.createElement('button');
            printBtn.innerHTML = '🖨️ Print/Save as PDF';
            printBtn.style.cssText = `
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: #007AFF;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 25px;
                font-weight: 600;
                cursor: pointer;
                box-shadow: 0 4px 15px rgba(0, 122, 255, 0.3);
                z-index: 1000;
                font-family: 'Inter', sans-serif;
            `;
            printBtn.onclick = () => window.print();
            document.body.appendChild(printBtn);
            
            // Add download as HTML button
            const downloadBtn = document.createElement('button');
            downloadBtn.innerHTML = '💾 Download HTML';
            downloadBtn.style.cssText = `
                position: fixed;
                bottom: 70px;
                right: 20px;
                background: #34C759;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 25px;
                font-weight: 600;
                cursor: pointer;
                box-shadow: 0 4px 15px rgba(52, 199, 89, 0.3);
                z-index: 1000;
                font-family: 'Inter', sans-serif;
            `;
            downloadBtn.onclick = () => {{
                const htmlContent = document.documentElement.outerHTML;
                const blob = new Blob([htmlContent], {{ type: 'text/html' }});
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'Android-EDR_Report_{ts}.html';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            }};
            document.body.appendChild(downloadBtn);
        }});
    </script>
</body>
</html>"""
    return html

def generate_text_report(data):
    """Generate a formatted text report from JSON data"""
    ts = data.get("timestamp", "unknown")
    dt = datetime.fromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M:%S")
    
    lines = []
    lines.append("=" * 80)
    lines.append(f"ANDROID-EDR SECURITY REPORT")
    lines.append("=" * 80)
    lines.append(f"Generated: {dt}")
    lines.append(f"Report ID: {ts}")
    lines.append("-" * 80)
    
    # Summary
    findings = data.get("findings", [])
    events = data.get("events", [])
    
    # Count severities
    severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for f in findings:
        sev = f.get("severity", "low").lower()
        severity_counts[sev] = severity_counts.get(sev, 0) + 1
    
    lines.append("REPORT SUMMARY:")
    lines.append(f"  Total Findings: {len(findings)}")
    lines.append(f"  Critical: {severity_counts['critical']}")
    lines.append(f"  High: {severity_counts['high']}")
    lines.append(f"  Medium: {severity_counts['medium']}")
    lines.append(f"  Low: {severity_counts['low']}")
    lines.append(f"  Events Logged: {len(events)}")
    lines.append("")
    
    # Device info if available
    device_info = data.get("device_info", {})
    if device_info:
        lines.append("DEVICE INFORMATION:")
        for key, value in device_info.items():
            if value:
                lines.append(f"  {key.replace('_', ' ').title()}: {value}")
        lines.append("")
    
    # Findings details
    if findings:
        lines.append("DETAILED FINDINGS:")
        lines.append("-" * 80)
        
        for i, finding in enumerate(findings, 1):
            lines.append(f"\nFINDING {i}:")
            lines.append(f"  Title: {finding.get('title', 'No title')}")
            lines.append(f"  Type: {finding.get('type', 'Unknown')}")
            lines.append(f"  Severity: {finding.get('severity', 'low').upper()}")
            lines.append(f"  Module: {finding.get('module', 'N/A')}")
            lines.append(f"  Rule: {finding.get('rule', 'N/A')}")
            
            if finding.get('path'):
                lines.append(f"  Path: {finding.get('path')}")
                if finding.get('line'):
                    lines.append(f"  Line: {finding.get('line')}")
            
            if finding.get('summary'):
                lines.append(f"  Summary: {finding.get('summary')}")
            
            if finding.get('detail'):
                lines.append(f"  Details:")
                detail_lines = str(finding.get('detail')).split('\n')
                for dl in detail_lines:
                    lines.append(f"    {dl}")
            
            lines.append("-" * 40)
    else:
        lines.append("No security findings detected.")
        lines.append("")
    
    # Events summary
    if events:
        lines.append("\nRECENT EVENTS LOG:")
        lines.append("-" * 80)
        for i, event in enumerate(events[:50], 1):
            event_type = event.get('type', 'Unknown')
            event_data = event.get('data', {})
            event_time = event.get('timestamp', '')
            if event_time:
                try:
                    event_time = datetime.fromtimestamp(int(event_time)).strftime("%H:%M:%S")
                except:
                    pass
            
            lines.append(f"{i:3d}. [{event_time}] {event_type}")
            if event_data:
                data_str = str(event_data)
                if len(data_str) > 100:
                    data_str = data_str[:97] + "..."
                lines.append(f"     Data: {data_str}")
    
    lines.append("")
    lines.append("=" * 80)
    lines.append("Generated by Android-EDR | Made by HAYSHAN")
    lines.append("=" * 80)
    
    return "\n".join(lines)

# Utility to safely escape HTML content for display
def escapeHtml(s):
    if not s:
        return ""
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


# ---------- UI (Tailwind Style) ----------
INDEX_HTML = r'''
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Android-EDR — Dashboard</title>
<script src="https://cdn.tailwindcss.com"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<script>
tailwind.config = {
  theme: {
    extend: {
      colors: {
        primary: '#007AFF',
        success: '#34C759',
        warning: '#FF9500',
        danger: '#FF3B30',
        dark: '#1C1C1E',
        light: '#F2F2F7',
        gray: {
          100: '#F9FAFB',
          200: '#F2F4F7',
          300: '#E5E7EB',
          400: '#D1D5DB',
          500: '#9CA3AF',
          600: '#6B7280',
          700: '#4B5563',
          800: '#374151',
          900: '#1F2937'
        }
      },
      fontFamily: {
        sans: ['SF Pro Display', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', 'sans-serif']
      }
    }
  }
}
</script>
<style>
@import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@400;500;600;700&display=swap');
body {
  background: linear-gradient(135deg, #f0f4ff 0%, #e6f0ff 100%);
  font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}
.card {
  background: white;
  border-radius: 20px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.03);
  border: 1px solid rgba(0, 0, 0, 0.02);
}

.btn {
  border-radius: 12px;
  font-weight: 600;
  padding: 10px 16px;
  transition: all 0.2s ease;
}

.btn-primary {
  background: #007AFF;
  color: white;
}

.btn-outline {
  background: transparent;
  border: 1px solid #007AFF;
  color: #007AFF;
}

.btn-danger {
  background: #FF3B30;
  color: white;
}

.btn-danger:hover {
  background: #E6352B;
}

.report-item {
  transition: all 0.2s ease;
  border-radius: 16px;
  cursor: pointer;
}

.report-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 122, 255, 0.1);
}

.accordion-header {
  border-radius: 16px;
  transition: all 0.2s ease;
}

.accordion-header:hover {
  background-color: #f8f9fc;
}

/* Custom styles for the details panel - which replaces the old 'right card' */
.report-detail-panel {
  display: none; /* Initially hidden, shown on report click */
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: white; /* Will cover the list view on mobile */
  z-index: 50;
  overflow-y: auto;
  padding: 16px;
}

@media (min-width: 1024px) { /* On desktop/tablet, display side-by-side */
  .main-content-grid {
    display: grid;
    grid-template-columns: 1fr 2fr;
    gap: 24px;
    max-width: 1200px;
    margin: 0 auto;
  }
  .report-detail-panel {
    position: static;
    display: block;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.03);
    border: 1px solid rgba(0, 0, 0, 0.02);
    border-radius: 20px;
  }
}

.report-detail-panel.open {
  display: block;
}

.finding-evidence-block {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease-out;
}

.finding-evidence-block.open {
  max-height: 500px; /* Adjust as needed */
}

.badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.badge-critical {
  background-color: rgba(255, 59, 48, 0.1);
  color: #FF3B30;
}
.badge-high {
  background-color: rgba(255, 59, 48, 0.1);
  color: #FF3B30;
}

.badge-medium {
  background-color: rgba(255, 149, 0, 0.1);
  color: #FF9500;
}

.badge-low {
  background-color: rgba(52, 199, 89, 0.1);
  color: #34C759;
}

.empty-state {
  padding: 40px 20px;
  text-align: center;
}

.empty-state i {
  font-size: 48px;
  color: #D1D5DB;
  margin-bottom: 16px;
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: #CBD5E1;
  border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
  background: #94A3B8;
}

/* Modal overlay */
.modal-overlay {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 100;
  align-items: center;
  justify-content: center;
}

.modal-overlay.active {
  display: flex;
}

.modal-content {
  background: white;
  border-radius: 20px;
  padding: 24px;
  max-width: 400px;
  width: 90%;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.confirmation-dialog {
  text-align: center;
}

.confirmation-dialog i {
  font-size: 48px;
  color: #FF3B30;
  margin-bottom: 16px;
}

/* Tooltip */
.tooltip {
  position: relative;
  display: inline-block;
}

.tooltip .tooltiptext {
  visibility: hidden;
  width: 200px;
  background-color: #374151;
  color: #fff;
  text-align: center;
  border-radius: 6px;
  padding: 8px;
  position: absolute;
  z-index: 1;
  bottom: 125%;
  left: 50%;
  margin-left: -100px;
  opacity: 0;
  transition: opacity 0.3s;
  font-size: 12px;
}

.tooltip:hover .tooltiptext {
  visibility: visible;
  opacity: 1;
}
</style>

</head>
<body class="min-h-screen">
  <header class="p-4 bg-white shadow-sm">
    <div class="flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-400 to-indigo-500 flex items-center justify-center">
          <span class="text-white font-bold text-xl">A</span>
        </div>
        <div>
          <h1 class="text-xl font-semibold text-gray-900">Android-EDR</h1>
          <p class="text-xs text-gray-500">Enterprise Detection & Response</p>
        </div>
      </div>
      <div class="flex items-center space-x-3">
        <div class="tooltip">
          <button id="refreshBtn" class="p-2 rounded-full hover:bg-gray-100">
            <i class="fas fa-sync-alt text-gray-600"></i>
          </button>
          <span class="tooltiptext">Refresh Reports</span>
        </div>
        <div id="userBtn" class="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center cursor-pointer tooltip">
          <span id="userInitial" class="text-gray-700 font-medium">U</span>
          <span class="tooltiptext">Set Display Name</span>
        </div>
      </div>
    </div>
  </header>

  <main class="p-4">
    <div class="main-content-grid">
      <div id="reportsListWrapper">
        <div class="mb-6">
          <div class="relative">
            <i class="fas fa-search absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
            <input type="text" id="searchInput" placeholder="Search reports..."
                   class="w-full pl-12 pr-4 py-3 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent">
          </div>
          <div id="filterButtons" class="mt-3 flex space-x-2 overflow-x-auto pb-2">
            <button data-filter="all" class="filter-btn px-4 py-2 bg-blue-100 text-blue-700 rounded-full text-sm font-medium whitespace-nowrap">All Reports</button>
            <button data-filter="critical" class="filter-btn px-4 py-2 bg-white text-gray-700 rounded-full text-sm font-medium whitespace-nowrap">Critical</button>
            <button data-filter="high" class="filter-btn px-4 py-2 bg-white text-gray-700 rounded-full text-sm font-medium whitespace-nowrap">High</button>
            <button data-filter="medium" class="filter-btn px-4 py-2 bg-white text-gray-700 rounded-full text-sm font-medium whitespace-nowrap">Medium</button>
            <button data-filter="low" class="filter-btn px-4 py-2 bg-white text-gray-700 rounded-full text-sm font-medium whitespace-nowrap">Low</button>
          </div>
        </div>

        <div class="mb-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-semibold text-gray-900">Recent Reports</h2>
            <span id="reportCount" class="text-sm text-gray-500">0 reports</span>
          </div>
          <div id="reportsContainer" class="space-y-4">
            </div>

          <div id="emptyState" class="empty-state hidden card">
            <i class="fas fa-inbox"></i>
            <h3 class="text-lg font-medium text-gray-900 mb-1">No reports yet</h3>
            <p class="text-gray-500 mb-4">Run <span class="font-mono bg-gray-100 px-2 py-1 rounded">android-edr detect</span> to generate your first report</p>
            </div>
        </div>
      </div>

      <div id="reportDetailPanel" class="report-detail-panel card">
        <div id="reportDetailContent">
            <button id="backToListBtn" class="lg:hidden text-gray-600 hover:text-gray-900 mb-4">
              <i class="fas fa-arrow-left mr-2"></i>Back to List
            </button>

            <div id="detailHeader" class="mb-6">
                <div class="flex items-center justify-between">
                    <h2 id="detailTitle" class="text-2xl font-bold text-gray-900">Select a Report</h2>
                    <span id="detailCount" class="badge badge-low">0 Findings</span>
                </div>
                <p id="detailMeta" class="text-sm text-gray-500 mt-1">Details will appear here after selection.</p>
            </div>

            <div id="detailActions" class="flex space-x-2 mb-6 hidden">
              <div class="dropdown relative">
                <button id="downloadBtn" class="btn btn-primary text-sm px-4 py-2">
                  <i class="fas fa-download mr-2"></i>Download Report
                </button>
                <div id="downloadDropdown" class="absolute left-0 mt-2 w-48 bg-white rounded-xl shadow-lg border border-gray-200 z-50 hidden">
                  <a href="#" class="download-option block px-4 py-3 text-sm text-gray-700 hover:bg-gray-100 rounded-t-xl" data-format="html">
                    <i class="fas fa-file-code mr-2 text-blue-500"></i>HTML Report (Best)
                  </a>
                  <a href="#" class="download-option block px-4 py-3 text-sm text-gray-700 hover:bg-gray-100" data-format="text">
                    <i class="fas fa-file-alt mr-2 text-green-500"></i>Text Report
                  </a>
                  <a href="#" class="download-option block px-4 py-3 text-sm text-gray-700 hover:bg-gray-100 rounded-b-xl" data-format="json">
                    <i class="fas fa-code mr-2 text-purple-500"></i>Raw JSON
                  </a>
                </div>
              </div>
              <button id="deleteReportBtn" class="btn btn-danger text-sm px-4 py-2">
                <i class="fas fa-trash mr-2"></i>Delete Report
              </button>
            </div>

            <div id="findingsContainer" class="space-y-4">
                <div id="detailEmpty" class="empty-state">
                  <i class="fas fa-hand-pointer"></i>
                  <p class="text-gray-500">Select a report from the list to view its findings and events.</p>
                </div>
                </div>

            <div id="eventsContainer" class="mt-8 border-t pt-4 hidden">
                <h3 class="text-lg font-semibold text-gray-900 mb-3">Events Log (Latest 50)</h3>
                <div id="eventsList" class="space-y-2 text-sm max-h-96 overflow-y-auto">
                    </div>
            </div>
        </div>
      </div>
    </div>
  </main>

  <!-- Confirmation Modal -->
  <div id="confirmationModal" class="modal-overlay">
    <div class="modal-content">
      <div class="confirmation-dialog">
        <i class="fas fa-exclamation-triangle"></i>
        <h3 class="text-lg font-semibold text-gray-900 mb-2">Delete Report?</h3>
        <p class="text-gray-600 mb-6">Are you sure you want to delete this report? This action cannot be undone.</p>
        <div class="flex space-x-3">
          <button id="confirmCancelBtn" class="btn btn-outline flex-1">Cancel</button>
          <button id="confirmDeleteBtn" class="btn btn-danger flex-1">Delete</button>
        </div>
      </div>
    </div>
  </div>

  <script>
    const API = {
      list: "/api/reports",
      report: (ts)=>`/api/report/${ts}`,
      reportHtml: (ts)=>`/api/report/${ts}/html`,
      reportText: (ts)=>`/api/report/${ts}/text`,
      deleteReport: (ts)=>`/api/report/${ts}`,
      setname: "/api/setname",
      user: "/api/user"
    };

    // Global state for reports
    let reportsCache = [];
    let currentFilter = 'all';
    let currentReportTs = null;

    // DOM Elements
    const reportsContainer = document.getElementById('reportsContainer');
    const reportCountEl = document.getElementById('reportCount');
    const emptyState = document.getElementById('emptyState');
    const searchInput = document.getElementById('searchInput');
    const refreshBtn = document.getElementById('refreshBtn');
    const userInitialEl = document.getElementById('userInitial');
    const userBtn = document.getElementById('userBtn');
    const filterButtons = document.querySelectorAll('.filter-btn');

    // Detail View Elements
    const reportDetailPanel = document.getElementById('reportDetailPanel');
    const backToListBtn = document.getElementById('backToListBtn');
    const detailTitleEl = document.getElementById('detailTitle');
    const detailMetaEl = document.getElementById('detailMeta');
    const detailCountEl = document.getElementById('detailCount');
    const detailActions = document.getElementById('detailActions');
    const downloadBtn = document.getElementById('downloadBtn');
    const downloadDropdown = document.getElementById('downloadDropdown');
    const deleteReportBtn = document.getElementById('deleteReportBtn');
    const findingsContainer = document.getElementById('findingsContainer');
    const eventsContainer = document.getElementById('eventsContainer');
    const eventsList = document.getElementById('eventsList');
    const detailEmptyEl = document.getElementById('detailEmpty');

    // Confirmation Modal Elements
    const confirmationModal = document.getElementById('confirmationModal');
    const confirmCancelBtn = document.getElementById('confirmCancelBtn');
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');

    // API Utility
    async function fetchJSON(url, opts){
      try{
        const r = await fetch(url, opts);
        if(!r.ok) throw new Error("HTTP " + r.status);
        return await r.json();
      }catch(e){
        console.error("fetch err", e);
        // Simple UI error indicator
        refreshBtn.innerHTML = '<i class="fas fa-exclamation-triangle text-danger"></i>';
        return null;
      }
    }

    async function fetchDelete(url) {
      try {
        const r = await fetch(url, { method: 'DELETE' });
        if(!r.ok) throw new Error("HTTP " + r.status);
        return await r.json();
      } catch(e) {
        console.error("delete err", e);
        return { ok: false, error: e.message };
      }
    }

    // Formatting Utilities
    function formatTS(ts){
      try{ return new Date(ts*1000).toLocaleString(); } catch(e){ return String(ts); }
    }

    function capitalize(s) {
      if (typeof s !== 'string') return '';
      return s.charAt(0).toUpperCase() + s.slice(1);
    }

    // Escape HTML function (was missing in JavaScript)
    function escapeHtml(text) {
      if (!text) return '';
      const div = document.createElement('div');
      div.textContent = text;
      return div.innerHTML;
    }

    // Helper function to get icons based on meta key (from your new HTML)
    function getIcon(key) {
      const icons = {
        device: 'mobile-alt',
        time: 'clock',
        endpoint: 'wifi',
        size: 'exclamation-triangle',
        package: 'shield-alt',
        risk: 'battery-quarter',
        number: 'sms',
        cost: 'dollar-sign',
        version: 'code-branch',
        cve: 'bug',
        impact: 'exclamation-triangle',
        data: 'database',
        destination: 'map-marker-alt',
        service: 'cogs',
        purpose: 'bullseye',
        method: 'tools',
        target: 'crosshairs',
        build: 'tools',
      };
      return icons[key.toLowerCase()] || 'info-circle';
    }

    // User Profile
    async function updateUserName() {
      const u = await fetchJSON(API.user);
      const userName = u && u.name ? u.name : "User";

      const initial = userName.split(' ').map(n => n[0]).join('').toUpperCase() || 'U';
      userInitialEl.textContent = initial;
      userInitialEl.setAttribute('title', userName); // Add tooltip
    }

    // Report Item Renderer
    function renderReports(reports) {
      const query = searchInput.value.toLowerCase();

      const filteredReports = reports.filter(report => {
        const severityMatch = currentFilter === 'all' || report.highest_severity === currentFilter;

        if (!query) return severityMatch;

        const queryMatch = String(report.ts).includes(query) ||
                           report.highest_severity.includes(query) ||
                           String(report.summary_count).includes(query);

        return severityMatch && queryMatch;
      });

      reportCountEl.textContent = `${filteredReports.length} reports`;

      if (filteredReports.length === 0) {
        emptyState.classList.remove('hidden');
        reportsContainer.innerHTML = '';
        return;
      }

      emptyState.classList.add('hidden');
      reportsContainer.innerHTML = '';

      filteredReports.forEach(report => {
        const severity = report.highest_severity;
        const severityClass = severity === 'critical' || severity === 'high' ? 'badge-high' :
                              severity === 'medium' ? 'badge-medium' : 'badge-low';
        const severityText = capitalize(severity);

        const node = document.createElement("div");
        node.className = "report-item card p-4";
        node.setAttribute('data-ts', report.ts);

        node.innerHTML = `
          <div class="flex justify-between items-start">
            <div>
              <div class="flex items-center space-x-2">
                <h3 class="font-medium text-gray-900">Report #${report.ts}</h3>
                <span class="badge ${severityClass}">${severityText}</span>
              </div>
              <p class="text-sm text-gray-500 mt-1">${formatTS(report.ts)}</p>
            </div>
            <div class="text-right">
              <div class="font-semibold text-gray-900">${report.summary_count} findings</div>
              <div class="mt-1 flex space-x-1">
                <button class="btn btn-outline text-xs px-3 py-1.5 view-report-btn">View</button>
                <button class="btn btn-danger text-xs px-3 py-1.5 delete-report-btn">
                  <i class="fas fa-trash"></i>
                </button>
              </div>
            </div>
          </div>
        `;
        reportsContainer.appendChild(node);

        node.querySelector(".view-report-btn").addEventListener("click", (e) => {
             e.stopPropagation();
             loadReport(report.ts);
        });

        node.querySelector(".delete-report-btn").addEventListener("click", (e) => {
             e.stopPropagation();
             showDeleteConfirmation(report.ts);
        });

        node.addEventListener("click", () => loadReport(report.ts));
      });
    }

    // Finding Card Renderer (Simplified for API data)
    function createFindingElement(finding, index) {
        const f = finding;
        const severity = (f.severity || "low").toLowerCase();
        const severityText = capitalize(severity);
        const severityClass = severity === 'critical' || severity === 'high' ? 'badge-high' :
                              severity === 'medium' ? 'badge-medium' : 'badge-low';

        const borderClass = severity === 'critical' || severity === 'high' ? 'border-red-500' :
                            severity === 'medium' ? 'border-orange-500' : 'border-blue-500';

        // Construct the meta data for display
        const metaData = {};
        if (f.module) metaData.Module = f.module;
        if (f.type) metaData.Type = f.type;
        if (f.rule) metaData.Rule = f.rule;
        if (f.path) metaData.Path = f.path;
        if (f.line) metaData.Line = f.line;
        if (f.ts) metaData.Time = formatTS(f.ts).split(', ')[1]; // Extract just the time

       // Extract detailed evidence, either from 'detail' or stringifying the whole object
        let details = f.detail || JSON.stringify(f, null, 2);

        const findingElement = document.createElement('div');
        findingElement.className = "border-l-4 " + borderClass + " pl-4 py-2 cursor-pointer finding-item";
        findingElement.setAttribute('data-index', index);

        findingElement.innerHTML = `
            <div class="flex justify-between items-start">
                <div>
                    <h5 class="font-medium text-gray-900">${f.title || capitalize(f.type || 'Finding')}</h5>
                    <p class="text-sm text-gray-600 mt-1">${f.summary || f.path || 'No summary provided'}</p>
                </div>
                <span class="badge ${severityClass} whitespace-nowrap">${severityText}</span>
            </div>

            <div class="mt-2 flex flex-wrap items-center text-xs text-gray-500">
                ${Object.entries(metaData).map(([key, value]) =>
                    `<span class="flex items-center mr-3"><i class="fas fa-${getIcon(key)} mr-1"></i> ${key}: ${value}</span>`
                ).join('')}
            </div>

            <div class="mt-4 finding-evidence-block" id="evidence-finding-${index}">
                <pre class="bg-gray-100 p-3 rounded-lg text-xs overflow-x-auto whitespace-pre-wrap">${escapeHtml(details)}</pre>
            </div>
        `;

        findingElement.addEventListener('click', function() {
          const evidenceBlock = document.getElementById(`evidence-finding-${index}`);
          const isOpen = evidenceBlock.classList.toggle('open');
          // Add/remove a visual highlight for the currently open finding
          findingElement.classList.toggle('bg-gray-50', isOpen);
        });

        return findingElement;
    }

    // Download report function
    function downloadReport(format) {
        if (!currentReportTs) return;
        
        let url, filename;
        switch(format) {
            case 'html':
                url = API.reportHtml(currentReportTs);
                filename = `Android-EDR_Report_${currentReportTs}.html`;
                break;
            case 'text':
                url = API.reportText(currentReportTs);
                filename = `Android-EDR_Report_${currentReportTs}.txt`;
                break;
            case 'json':
                url = API.report(currentReportTs);
                filename = `Android-EDR_Report_${currentReportTs}.json`;
                break;
            default:
                return;
        }
        
        // Create a hidden anchor element to trigger download
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }

    // Load Report Details
    async function loadReport(ts) {
        currentReportTs = ts;
        
        // Find the report in cache to get summary data
        const summary = reportsCache.find(r => String(r.ts) === String(ts));

        if (!summary) {
            console.error("Report summary not found in cache for TS:", ts);
            return;
        }

        // Show loading state
        detailTitleEl.textContent = `Loading Report #${ts}...`;
        detailMetaEl.textContent = 'Fetching details from server...';
        detailCountEl.textContent = '...';
        findingsContainer.innerHTML = '';
        eventsContainer.classList.add('hidden');
        detailActions.classList.add('hidden');
        detailEmptyEl.classList.add('hidden');

        // Toggle to detail view on mobile
        reportDetailPanel.classList.add('open');

        // Fetch full report data
        const data = await fetchJSON(API.report(ts));

        if (!data || data.error) {
            detailTitleEl.textContent = `Error Loading Report #${ts}`;
            detailMetaEl.textContent = 'Failed to fetch report data.';
            return;
        }

        // Update Header
        detailTitleEl.textContent = `Report #${ts}`;
        detailMetaEl.textContent = `Saved: ${formatTS(data.timestamp)}`;
        const findingCount = (data.findings || []).length;
        detailCountEl.textContent = `${findingCount} Findings`;
        detailCountEl.className = 'badge ' + (summary.highest_severity === 'critical' || summary.highest_severity === 'high' ? 'badge-high' : summary.highest_severity === 'medium' ? 'badge-medium' : 'badge-low');

        // Show action buttons
        detailActions.classList.remove('hidden');

        // Render Findings
        if (findingCount > 0) {
            findingsContainer.innerHTML = '';
            (data.findings || []).forEach((finding, index) => {
                findingsContainer.appendChild(createFindingElement(finding, index));
            });
        } else {
            detailEmptyEl.classList.remove('hidden');
            detailEmptyEl.querySelector('i').className = 'fas fa-check-circle text-success';
            detailEmptyEl.querySelector('p').textContent = 'No findings were detected in this report. Looks clean!';
            findingsContainer.innerHTML = '';
        }

        // Render Events
        if (data.events && data.events.length > 0) {
            eventsContainer.classList.remove('hidden');
            eventsList.innerHTML = '';
            data.events.slice(0, 50).forEach(event => {
                const eventEl = document.createElement('div');
                eventEl.className = 'bg-white p-3 rounded-lg shadow-sm';
                eventEl.innerHTML = `<span class="font-medium text-gray-800">${event.type}</span>: <span class="text-gray-600">${JSON.stringify(event.data).slice(0, 100)}...</span>`;
                eventsList.appendChild(eventEl);
            });
        } else {
            eventsContainer.classList.add('hidden');
        }
    }

    // Delete Report Functions
    function showDeleteConfirmation(ts) {
        currentReportTs = ts;
        confirmationModal.classList.add('active');
    }

    async function deleteCurrentReport() {
        if (!currentReportTs) return;
        
        const result = await fetchDelete(API.deleteReport(currentReportTs));
        
        if (result && result.ok) {
            // Remove from cache
            reportsCache = reportsCache.filter(r => String(r.ts) !== String(currentReportTs));
            
            // Update UI
            renderReports(reportsCache);
            
            // Close detail view if open
            if (reportDetailPanel.classList.contains('open')) {
                reportDetailPanel.classList.remove('open');
                detailActions.classList.add('hidden');
                detailEmptyEl.classList.remove('hidden');
                detailEmptyEl.querySelector('i').className = 'fas fa-hand-pointer';
                detailEmptyEl.querySelector('p').textContent = 'Select a report from the list to view its findings and events.';
                detailTitleEl.textContent = 'Select a Report';
                detailMetaEl.textContent = 'Details will appear here after selection.';
                detailCountEl.textContent = '0 Findings';
                detailCountEl.className = 'badge badge-low';
            }
            
            // Show success message
            alert('Report deleted successfully!');
        } else {
            alert('Failed to delete report: ' + (result.error || 'Unknown error'));
        }
        
        confirmationModal.classList.remove('active');
        currentReportTs = null;
    }

    // Main Render Function (fetches report list)
    async function mainRender() {
      // Refresh button spinner
      refreshBtn.innerHTML = '<i class="fas fa-sync-alt fa-spin text-gray-600"></i>';

      await updateUserName(); // Update username/initial

      const arr = await fetchJSON(API.list);

      // Stop spinner
      refreshBtn.innerHTML = '<i class="fas fa-sync-alt text-gray-600"></i>';

      if(arr){
        reportsCache = arr;
        renderReports(reportsCache);
      } else {
         // Show error or empty state if API call failed
         reportsCache = [];
         renderReports([]);
      }
    }

    // Event Listeners and Initialization
    document.addEventListener('DOMContentLoaded', () => {
      // Initial render
      mainRender();

      // Auto-refresh every 10 seconds
      setInterval(mainRender, 10000);

      // Search functionality (re-render reports from cache)
      searchInput.addEventListener('input', () => renderReports(reportsCache));

      // Filter functionality
      filterButtons.forEach(btn => {
        btn.addEventListener('click', function() {
          filterButtons.forEach(b => {
             b.classList.remove('bg-blue-100', 'text-blue-700');
             b.classList.add('bg-white', 'text-gray-700');
          });
          this.classList.add('bg-blue-100', 'text-blue-700');
          this.classList.remove('bg-white', 'text-gray-700');
          currentFilter = this.getAttribute('data-filter');
          renderReports(reportsCache);
        });
      });

      // Refresh button
      refreshBtn.addEventListener('click', mainRender);

      // User button (Set Name)
      userBtn.addEventListener('click', async ()=>{
        const name = prompt("Your display name:");
        if(!name) return;
        await fetch(API.setname, {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({name})});
        await updateUserName();
      });

      // Mobile back button
      backToListBtn.addEventListener('click', () => {
         reportDetailPanel.classList.remove('open');
      });

      // Delete report button
      deleteReportBtn.addEventListener('click', () => {
        if (currentReportTs) {
            showDeleteConfirmation(currentReportTs);
        }
      });

      // Download button dropdown
      downloadBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        downloadDropdown.classList.toggle('hidden');
      });

      // Download option selection
      document.querySelectorAll('.download-option').forEach(option => {
        option.addEventListener('click', (e) => {
          e.preventDefault();
          const format = e.currentTarget.getAttribute('data-format');
          downloadReport(format);
          downloadDropdown.classList.add('hidden');
        });
      });

      // Close dropdown when clicking outside
      document.addEventListener('click', () => {
        downloadDropdown.classList.add('hidden');
      });

      // Confirmation modal buttons
      confirmCancelBtn.addEventListener('click', () => {
        confirmationModal.classList.remove('active');
        currentReportTs = null;
      });

      confirmDeleteBtn.addEventListener('click', deleteCurrentReport);

      // Close modal when clicking outside
      confirmationModal.addEventListener('click', (e) => {
        if (e.target === confirmationModal) {
          confirmationModal.classList.remove('active');
          currentReportTs = null;
        }
      });
    });
  </script>
</body>
</html>
'''

# ---------- HTTP handler ----------
class Handler(http.server.SimpleHTTPRequestHandler):
    def _send_json(self, obj, code=200):
        b = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)
    
    def _send_text(self, text, filename="report.txt", code=200):
        b = text.encode('utf-8')
        self.send_response(code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)
    
    def _send_html(self, html, filename="report.html", code=200):
        b = html.encode('utf-8')
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        path = urllib.parse.unquote(self.path)
        # root UI
        if path == "/" or path == "/index.html":
            body = INDEX_HTML.encode('utf-8')
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if path == "/api/reports":
            reports = list_reports()
            self._send_json(reports)
            return

        if path.startswith("/api/report/"):
            parts = path.split("/")
            ts = parts[3] if len(parts) > 3 else None
            
            if not ts:
                self._send_json({"error":"no timestamp provided"}, code=400)
                return
            
            # Check if it's an HTML report request
            if len(parts) > 4 and parts[4] == "html":
                rpt = read_report(ts)
                if rpt is None:
                    self._send_json({"error":"not found"}, code=404)
                else:
                    try:
                        html_report = generate_html_report(rpt)
                        filename = f"Android-EDR_Report_{ts}.html"
                        self._send_html(html_report, filename)
                    except Exception as e:
                        print(f"[ERROR] HTML generation failed: {str(e)}")
                        import traceback
                        traceback.print_exc()
                        self._send_text(f"HTML generation failed: {str(e)}\n{traceback.format_exc()}", code=500)
                return
            
            # Check if it's a text report request
            if len(parts) > 4 and parts[4] == "text":
                rpt = read_report(ts)
                if rpt is None:
                    self._send_json({"error":"not found"}, code=404)
                else:
                    try:
                        text_report = generate_text_report(rpt)
                        filename = f"Android-EDR_Report_{ts}.txt"
                        self._send_text(text_report, filename)
                    except Exception as e:
                        print(f"[ERROR] Text generation failed: {str(e)}")
                        import traceback
                        traceback.print_exc()
                        self._send_text(f"Text generation failed: {str(e)}\n{traceback.format_exc()}", code=500)
                return
            
            # Regular JSON report
            rpt = read_report(ts)
            if rpt is None:
                self._send_json({"error":"not found"}, code=404)
            else:
                self._send_json(rpt)
            return

        if path == "/api/user":
            name = get_username()
            self._send_json({"name": name})
            return

        # fallback
        self.send_error(404, "Not found")
    
    def do_DELETE(self):
        path = urllib.parse.unquote(self.path)
        
        if path.startswith("/api/report/"):
            parts = path.split("/")
            ts = parts[3] if len(parts) > 3 else None
            if not ts:
                self._send_json({"error":"no timestamp provided"}, code=400)
                return
            
            if delete_report(ts):
                self._send_json({"ok": True})
            else:
                self._send_json({"ok": False, "error": "Failed to delete report"}, code=500)
            return
        
        self.send_error(404, "Not found")

    def do_POST(self):
        path = urllib.parse.unquote(self.path)
        length = int(self.headers.get('Content-Length', 0))
        raw = self.rfile.read(length) if length else b""
        # parse JSON first
        payload = {}
        if raw:
            try:
                payload = json.loads(raw.decode('utf-8'))
            except Exception:
                try:
                    # Fallback to form-encoded data, needed for robustness
                    parsed_qs = urllib.parse.parse_qs(raw.decode('utf-8'))
                    # Convert list of values to single value if possible
                    payload = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in parsed_qs.items()}
                except Exception:
                    payload = {}

        if path == "/api/setname":
            name = payload.get("name")
            if not name:
                self._send_json({"error":"no name provided"}, code=400)
                return
            ok = set_username(name)
            if ok:
                self._send_json({"ok":True})
            else:
                self._send_json({"ok":False}, code=500)
            return

        self.send_error(404, "Not found")

def start_dashboard(host=HOST, port=PORT):
    ensure_report_dir()
    addr = (host, port)
    print(f"[dashboard] Serving on http://{addr[0]}:{addr[1]}  (Ctrl+C to stop)")
    print("[dashboard] Reports directory:", str(REPORT_DIR))
    print("[dashboard] Features:")
    print("  ✓ Delete reports with confirmation")
    print("  ✓ HTML report downloads (print as PDF)")
    print("  ✓ Text report downloads")
    print("  ✓ Evidence display")
    print("  ✓ Real-time updates")
    print("  ✓ Made by HAYSHAN watermark")
    print("\nDownload URLs:")
    print("  HTML: http://127.0.0.1:8080/api/report/<timestamp>/html")
    print("  Text: http://127.0.0.1:8080/api/report/<timestamp>/text")
    print("  JSON: http://127.0.0.1:8080/api/report/<timestamp>")
    
    with socketserver.TCPServer(addr, Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[dashboard] Stopping server")
            httpd.server_close()

if __name__ == "__main__":
    # Allow optional host/port args
    h = HOST; p = PORT
    if len(sys.argv) >= 2:
        try:
            p = int(sys.argv[1])
        except:
            pass
    start_dashboard(host=h, port=p)
