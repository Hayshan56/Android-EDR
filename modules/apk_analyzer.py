#!/usr/bin/env python3
"""
modules/apk_analyzer.py
Lightweight static APK analyzer for Termux (no aapt dependency).
This is a best-effort analyzer: extracts filename, size, and does simple string checks.
Provides:
 - run_once(apk_path, verbose=False)
 - analyze_apk(apk_path, verbose=False)
"""
from utils.logger import info, warn, error
from pathlib import Path
import json
import time

REPORTS = Path("reports")
REPORTS.mkdir(exist_ok=True)

def analyze_apk(apk_path, verbose=False):
    p = Path(apk_path)
    if not p.exists():
        error(f"[apk_analyzer] APK not found: {apk_path}")
        return None

    info(f"[apk_analyzer] Analyzing {apk_path}")
    report = {
        "timestamp": int(time.time()),
        "apk": str(p.name),
        "path": str(p.resolve()),
        "size_bytes": p.stat().st_size,
        "strings_hits": [],
        "permissions_guess": [],
        "summary": {
            "risk_score": 0,
            "notes": ""
        }
    }

    # quick string scan (not a full decompile)
    try:
        data = p.read_bytes()
        text = None
        try:
            text = data.decode(errors="ignore")
        except Exception:
            text = str(data[:10000])
        # suspicious keywords
        keywords = ["su", "frida", "dex", "exec", "Runtime.getRuntime", "java.lang.Runtime", "getRuntime", "shell", "su\x00"]
        for kw in keywords:
            if kw in text:
                report["strings_hits"].append(kw)
        # naive permission guesses from manifest-like strings
        perm_keys = ["android.permission", "READ_SMS", "SEND_SMS", "RECEIVE_SMS", "RECORD_AUDIO"]
        for pk in perm_keys:
            if pk in text:
                report["permissions_guess"].append(pk)
        # crude risk score
        report["summary"]["risk_score"] = min(100, len(report["strings_hits"]) * 10 + len(report["permissions_guess"]) * 8)
    except Exception as e:
        error(f"[apk_analyzer] error reading apk: {e}")
        report["summary"]["notes"] = f"error:{e}"

    # save report
    outdir = REPORTS / "apk_analysis"
    outdir.mkdir(exist_ok=True)
    fname = outdir / f"{report['apk']}_{report['timestamp']}.json"
    try:
        fname.write_text(json.dumps(report, indent=2))
        info(f"[apk_analyzer] Saved report: {fname}")
    except Exception as e:
        error(f"[apk_analyzer] failed save: {e}")
    return report

def run_once(apk_path, verbose=False):
    return analyze_apk(apk_path, verbose=verbose)
