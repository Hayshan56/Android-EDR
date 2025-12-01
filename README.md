# Android-EDR (Termux Edition)

Android-EDR is an **enterprise-style Endpoint Detection & Response system** designed to run locally inside **Termux** on Android devices.  
It focuses on offline, rule-based + anomaly-based detection, and lightweight APK static analysis.

---

## 🔥 Features

- Process monitoring (live snapshot)
- Network socket analysis + rules engine
- File scanning & integrity hints
- Persistence detection (init.d, boot receivers)
- Root / Magisk indicators detection
- Signature-based malware checks
- Rule-based behavior correlation (v1 / v2)
- Baseline-based anomaly detection
- APK static analyzer (manifest & libs)
- JSON / TXT / HTML report generation

---

## 📦 Requirements (Termux)

Termux packages:
```bash
pkg update -y
pkg upgrade -y
pkg install -y python git curl nano openssh clang

Python packages:

requests
colorama
pyyaml
rich

You can install them with:

pip install -r requirements.txt


---

🚀 Install (Termux)

git clone https://github.com/Hayshan56/Android-EDR.git
cd Android-EDR
bash install.sh

install.sh will:

install (or ensure) dependencies

copy the launcher into $PREFIX/bin/android-edr

make launcher executable

create reports/ and logs/ directories



---

🧭 Usage

Run via the installed launcher:

# Single detection pass
android-edr detect --verbose

# Continuous monitoring (daemon style from shell)
android-edr monitor --interval 8 --verbose

# Static APK analysis
android-edr analyze /sdcard/Download/app.apk --verbose

# Extended help
android-edr full-help

Or run core directly:

python3 core/main.py detect --verbose
python3 core/main.py monitor --interval 8 --verbose


---

📁 Project layout (short)

core/                 # engine, monitor, scheduler, event bus
modules/              # detection modules (process, network, file, apk, etc.)
utils/                # logger, storage, helpers, crypto, report builder
config/               # settings + baseline + rules
reports/              # generated scan reports
logs/                 # internal logs / scan dumps
tests/                # unit-test stubs
README.md
install.sh
requirements.txt
LICENSE


---

🧩 Reports

Reports generated under reports/ — JSON, TXT and optional HTML.

Example:

reports/
  report_163xxxx.json
  report_163xxxx.txt
  behavior_report.json
  baseline.json


---

⚖️ License

MIT License — see LICENSE file.


---

🛠️ Contributing

PRs welcome. Keep changes modular: add new detection modules under modules/ and register in core/engine.py or add integration via behavior_engine_v2.

