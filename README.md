Android-EDR 🛡️

<div align="center">

https://img.shields.io/badge/Android-EDR-Enterprise_Detection_Response-blue?style=for-the-badge&logo=android&logoColor=white
https://img.shields.io/badge/Termux-Compatible-green?style=for-the-badge&logo=termux&logoColor=white
https://img.shields.io/badge/Python-3.12%2B-blue?style=for-the-badge&logo=python&logoColor=white
https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge

Enterprise-style Endpoint Detection & Response System for Android Termux

"Security monitoring for the mobile-first world"

</div>

---

✨ Features Overview

🔍 Detection & Monitoring

Feature Status Description
Process Monitoring ✅ Active Live snapshot of running processes
Network Analysis ✅ Active Socket analysis with rules engine
File Integrity Scanning ✅ Active File scanning & integrity checks
Persistence Detection ✅ Active Init.d, boot receivers, daemons
Root/Magisk Detection ✅ Active Root indicators & bypass attempts
Signature-based Scanning ✅ Active Known malware signature checks

🧠 Intelligence & Analysis

Feature Status Description
Behavior Correlation ✅ v2 Engine Rule-based behavior analysis
Anomaly Detection ✅ Baseline-based Statistical deviation detection
APK Static Analysis ✅ Deep Scan Manifest, libraries, permissions
Real-time Monitoring ✅ Daemon Mode Continuous threat detection
Multi-format Reporting ✅ JSON/TXT/HTML Professional report generation

🎯 Dashboard & Management

Feature Status Description
Web Dashboard ✅ Localhost:8080 Mobile-first UI with Tailwind CSS
Report Management ✅ View/Delete Interactive report browser
Evidence Viewer ✅ Expandable Detailed finding evidence display
Export Reports ✅ HTML/Text/JSON Professional report downloads
Real-time Updates ✅ Auto-refresh Live data without page reload

---

🚀 Quick Start

Termux Installation

```bash
# Update Termux packages
pkg update -y && pkg upgrade -y

# Install required packages
pkg install -y python git curl openssh clang

# Clone the repository
git clone https://github.com/Hayshan56/Android-EDR.git
cd Android-EDR

# Run installation script
bash install.sh

# Or install manually
pip install -r requirements.txt
```

One-Command Setup

```bash
# Complete installation in one command
curl -sL https://raw.githubusercontent.com/Hayshan56/Android-EDR/main/install.sh | bash
```

---

📖 Usage Guide

Basic Commands

```bash
# Run a single security scan
android-edr detect --verbose

# Monitor continuously (daemon mode)
android-edr monitor --interval 8 --verbose

# Analyze specific APK file
android-edr analyze /sdcard/Download/app.apk --verbose

# Start the web dashboard
android-edr dashboard

# Show full help
android-edr full-help
```

Direct Core Execution

```bash
# Run detection engine
python3 core/main.py detect --verbose

# Continuous monitoring
python3 core/main.py monitor --interval 8 --verbose

# Start dashboard server
python3 core/dashboard.py
```

---

🖥️ Web Dashboard

Access & Features

· URL: http://127.0.0.1:8080
· Port: 8080 (configurable)
· Authentication: None (localhost only)
· Auto-refresh: Every 10 seconds

Dashboard Features

```
✅ Mobile-first responsive design
✅ Real-time report listing
✅ Severity filtering (Critical/High/Medium/Low)
✅ Interactive evidence viewer
✅ Report deletion with confirmation
✅ Multiple export formats
✅ User-friendly interface
```

Report Download Options

```html
📄 HTML Report - Beautiful, printable, with HAYSHAN watermark
📝 Text Report - Plain text format
🔧 JSON Report - Raw data for analysis
```

---

🏗️ Project Architecture

```
Android-EDR/
├── core/                    # Core engine & dashboard
│   ├── main.py             # Main detection engine
│   ├── dashboard.py        # Web dashboard (HTML/API)
│   ├── engine.py           # Detection engine
│   ├── monitor.py          # Monitoring daemon
│   ├── scheduler.py        # Task scheduler
│   └── event_bus.py        # Event communication
│
├── modules/                # Detection modules
│   ├── process/           # Process monitoring
│   ├── network/          # Network analysis
│   ├── file/             # File integrity
│   ├── apk/              # APK static analysis
│   ├── persistence/      # Persistence detection
│   └── root/             # Root detection
│
├── utils/                 # Utilities & helpers
│   ├── logger.py         # Logging system
│   ├── storage.py        # Data storage
│   ├── report_builder.py # Report generation
│   ├── crypto.py         # Cryptographic functions
│   └── helpers.py        # Utility functions
│
├── config/                # Configuration
│   ├── settings.yaml     # Main settings
│   ├── baseline.json     # System baseline
│   └── rules/           # Detection rules
│
├── reports/              # Generated reports
├── logs/                # System logs
├── static/              # Static assets
└── tests/               # Test suites
```

---

📊 Report Structure

Sample Report (HTML)

```html
Android-EDR Security Report
├── Executive Summary
│   ├── Total Findings: 15
│   ├── Critical: 2
│   ├── High: 5
│   ├── Medium: 6
│   └── Low: 2
│
├── Device Information
│   ├── Model: Pixel 6
│   ├── Android Version: 13
│   └── Root Status: Not Rooted
│
├── Detailed Findings
│   ├── Finding #1: Suspicious Network Activity [CRITICAL]
│   ├── Finding #2: Unusual Process Behavior [HIGH]
│   └── Finding #3: Modified System File [MEDIUM]
│
└── Events Log (Last 50 events)
    └── Timestamped security events
```

Report Formats

Format Best For Features
HTML Human Reading Color-coded, printable, responsive
Text Quick Review Simple, fast, grep-friendly
JSON Automation Machine-readable, structured
Dashboard Live View Interactive, real-time

---

⚡ Performance & Optimization

Resource Usage

· Memory: ~50-100MB (typical)
· CPU: <5% during idle, ~15-30% during scan
· Storage: Minimal (~10MB + report storage)
· Network: Localhost only (no external calls)

Optimization Tips

```bash
# Run during low-usage periods
android-edr detect --quick

# Adjust monitoring interval
android-edr monitor --interval 15  # Less frequent checks

# Limit APK analysis depth
android-edr analyze app.apk --shallow

# Use text reports for speed
android-edr detect --format text
```

---

🛡️ Security Considerations

Isolation & Safety

```
🔒 Localhost-only - Dashboard runs on 127.0.0.1 only
🔒 No Internet Access - All analysis is offline
🔒 Read-Only Operations - No system modifications
🔒 Permission Boundaries - Respects Android permissions
🔒 Data Privacy - Reports stored locally only
```

Privacy Features

· No telemetry or data collection
· All processing happens on-device
· Reports contain only security findings
· No personal data in reports
· Configurable data retention

---

🤝 Contributing

We welcome contributions! Here's how:

Reporting Issues

1. Check existing issues
2. Create new issue with:
   · Android version
   · Termux version
   · Error logs
   · Steps to reproduce

Code Contributions

```bash
# Fork the repository
git clone your-fork-url
cd Android-EDR

# Create feature branch
git checkout -b feature/amazing-feature

# Make changes and commit
git commit -m "Add amazing feature"

# Push and create PR
git push origin feature/amazing-feature
```

Development Guidelines

· Keep modules independent
· Add tests for new features
· Update documentation
· Follow existing code style
· Add type hints where possible

---

📚 Documentation

Quick Reference

Command Description Example
detect Run security scan android-edr detect --verbose
monitor Continuous monitoring android-edr monitor --interval 10
analyze APK analysis android-edr analyze app.apk
dashboard Start web UI android-edr dashboard
help Show help android-edr full-help

Configuration Files

```yaml
# config/settings.yaml
monitoring:
  interval: 8
  enabled: true
  
detection:
  modules:
    - process
    - network
    - file
  
reporting:
  format: html
  retention_days: 30
```

---

🌟 Advanced Features

Custom Rules

```json
{
  "rule_id": "CUSTOM_001",
  "name": "Suspicious Process Pattern",
  "severity": "high",
  "condition": "process.cmdline CONTAINS 'miner'",
  "action": "alert"
}
```

Baseline Creation

```bash
# Create system baseline
android-edr detect --baseline

# Save baseline to file
android-edr detect --save-baseline baseline.json

# Use custom baseline
android-edr detect --baseline-file custom_baseline.json
```

Automation & Scheduling

```bash
# Cron job for daily scan
0 2 * * * android-edr detect --format text --output /sdcard/daily_report.txt

# Weekly deep scan
0 3 * * 0 android-edr detect --deep --format html
```

---

🚨 Troubleshooting

Common Issues

Problem Solution
Dashboard not loading Check port 8080 is free
Permission denied Grant storage permissions
Python errors Update Termux packages
Report generation fails Check disk space
Slow performance Reduce scan scope

Debug Mode

```bash
# Enable verbose logging
android-edr detect --verbose --debug

# Log to file
android-edr detect 2>&1 | tee scan.log

# Check system logs
cat ~/.aedr_logs/latest.log
```

---

📞 Support & Community

Getting Help

· GitHub Issues: Bug reports & feature requests
· Documentation: Check this README first
· Community: Termux security channels

Resources

· 📖 Termux Documentation
· 🐍 Python for Android
· 🔐 Mobile Security Resources

---

📄 License

```
MIT License
Copyright (c) 2024 HAYSHAN

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<div align="center">

Made with ❤️ by HAYSHAN

https://img.shields.io/badge/Android--EDR-Powered_By_Termux-blue?style=for-the-badge&logo=android
https://img.shields.io/badge/Built_For-Termux-green?style=for-the-badge&logo=gnu-bash
https://img.shields.io/badge/Powered_By-Python-yellow?style=for-the-badge&logo=python

Security shouldn't be complicated. It should be accessible.

</div>

---

🎯 What's Next?

Planned Features

· ✅ ~~Web Dashboard~~ DONE
· ✅ ~~Report Management~~ DONE
· 🔄 Mobile App Companion
· 🔄 Cloud Sync (Optional)
· 🔄 Advanced AI Detection
· 🔄 More Detection Modules

Get Involved

1. ⭐ Star the repository
2. 🐛 Report issues
3. 💡 Suggest features
4. 🔧 Submit pull requests
5. 📢 Share with others

---

<div align="center">

Stay secure. Stay vigilant. Stay protected.

Android-EDR - Enterprise security for everyone

</div>

---

Quick Links: Install | Usage | Dashboard | Reports | Contributing
