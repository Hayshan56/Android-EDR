
# Android-EDR 🛡️

[![IMG-20251206-095925.png](https://i.postimg.cc/c4QJBLq6/IMG-20251206-095925.png)](https://postimg.cc/6ypw9wpN)

[![Termux Compatible](https://img.shields.io/badge/Termux-Compatible-green?style=for-the-badge&logo=termux&logoColor=white)](https://termux.com/)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

**Enterprise-style Endpoint Detection & Response System for Android Termux**  
*"Security monitoring for the mobile-first world"*

---

## ✨ Features Overview

### 🔍 Detection & Monitoring

| Feature                  | Status | Description                          |
|--------------------------|--------|--------------------------------------|
| Process Monitoring       | ✅ Active | Live snapshot of running processes   |
| Network Analysis         | ✅ Active | Socket analysis with rules engine    |
| File Integrity Scanning  | ✅ Active | File scanning & integrity checks     |
| Persistence Detection    | ✅ Active | Init.d, boot receivers, daemons      |
| Root/Magisk Detection    | ✅ Active | Root indicators & bypass attempts    |
| Signature-based Scanning | ✅ Active | Known malware signature checks       |

### 🧠 Intelligence & Analysis

| Feature                 | Status | Description                                |
|-------------------------|--------|--------------------------------------------|
| Behavior Correlation    | ✅ v2 Engine | Rule-based behavior analysis           |
| Anomaly Detection       | ✅ Baseline-based | Statistical deviation detection  |
| APK Static Analysis     | ✅ Deep Scan | Manifest, libraries, permissions     |
| Real-time Monitoring    | ✅ Daemon Mode | Continuous threat detection         |
| Multi-format Reporting  | ✅ | JSON/TXT/HTML professional report generation |

### 🎯 Dashboard & Management

| Feature                 | Status | Description                               |
|-------------------------|--------|-------------------------------------------|
| Web Dashboard           | ✅ Localhost:8080 | Mobile-first UI with Tailwind CSS |
| Report Management       | ✅ | View/Delete interactive report browser    |
| Evidence Viewer         | ✅ | Expandable detailed finding evidence      |
| Export Reports          | ✅ | HTML/Text/JSON professional report downloads |
| Real-time Updates       | ✅ | Auto-refresh live data without page reload |

---

## 🚀 Quick Start

### Termux Installation

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

One-Command Setup

curl -sL https://raw.githubusercontent.com/Hayshan56/Android-EDR/main/install.sh | bash


---

📖 Usage Guide

Basic Commands

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

Direct Core Execution

# Run detection engine
python3 core/main.py detect --verbose

# Continuous monitoring
python3 core/main.py monitor --interval 8 --verbose

# Start dashboard server
python3 core/dashboard.py


---

🖥️ Web Dashboard

URL: http://127.0.0.1:8080

Port: 8080 (configurable)

Authentication: None (localhost only)

Auto-refresh: Every 10 seconds


Dashboard Features

✅ Mobile-first responsive design

✅ Real-time report listing

✅ Severity filtering (Critical/High/Medium/Low)

✅ Interactive evidence viewer

✅ Report deletion with confirmation

✅ Multiple export formats

✅ User-friendly interface


Report Download Options

📄 HTML Report - Beautiful, printable, with HAYSHAN watermark

📝 Text Report - Plain text format

🔧 JSON Report - Raw data for automation



---

🏗️ Project Architecture

Android-EDR/
├── core/
│   ├── main.py
│   ├── dashboard.py
│   ├── engine.py
│   ├── monitor.py
│   ├── scheduler.py
│   └── event_bus.py
├── modules/
│   ├── process/
│   ├── network/
│   ├── file/
│   ├── apk/
│   ├── persistence/
│   └── root/
├── utils/
│   ├── logger.py
│   ├── storage.py
│   ├── report_builder.py
│   ├── crypto.py
│   └── helpers.py
├── config/
│   ├── settings.yaml
│   ├── baseline.json
│   └── rules/
├── reports/
├── logs/
├── static/
└── tests/


---

⚡ Performance & Optimization

Memory: ~50-100MB

CPU: <5% idle, ~15-30% during scan

Storage: Minimal (~10MB + report storage)

Network: Localhost only


Optimization Tips

# Run during low-usage periods
android-edr detect --quick

# Adjust monitoring interval
android-edr monitor --interval 15

# Limit APK analysis depth
android-edr analyze app.apk --shallow

# Use text reports for speed
android-edr detect --format text


---

🛡️ Security Considerations

Localhost-only dashboard

No Internet access (offline analysis)

Read-only operations

Respects Android permission boundaries

Reports stored locally only


Privacy Features

No telemetry or data collection

All processing on-device

Reports contain only security findings

Configurable data retention



---

🤝 Contributing

Reporting Issues

1. Check existing issues


2. Create new issue with:

Android version

Termux version

Error logs

Steps to reproduce




Code Contributions

# Fork the repository
git clone your-fork-url
cd Android-EDR

# Create feature branch
git checkout -b feature/amazing-feature

# Make changes and commit
git commit -m "Add amazing feature"

# Push and create PR
git push origin feature/amazing-feature

Development Guidelines

Keep modules independent

Add tests for new features

Update documentation

Follow existing code style

Add type hints where possible



---

📄 License

MIT License © 2024 HAYSHAN

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, subject to the conditions in the LICENSE file.


---


Made with ❤️ by HAYSHAN 

Security shouldn't be complicated. It should be accessible.

Made By Ai I just also tell that here 
