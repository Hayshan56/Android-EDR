#!/usr/bin/env python3
"""
modules/process_monitor.py
Scans running processes and reports suspicious names or unusual command lines.
"""
import subprocess
import re
import time
from pathlib import Path

SUSPICIOUS_NAMES = ["su", "dd", "nc", "bash", "sh", "dropbear", "busybox"]

def _ps():
    try:
        out = subprocess.check_output(["ps","aux"], text=True, stderr=subprocess.DEVNULL)
        return out
    except Exception:
        try:
            return subprocess.check_output(["ps"], text=True, stderr=subprocess.DEVNULL)
        except Exception:
            return ""

def run_once(verbose=False):
    findings = []
    events = []
    txt = _ps()
    for ln in txt.splitlines():
        lower = ln.lower()
        for s in SUSPICIOUS_NAMES:
            if f" {s} " in f" {lower} " or lower.startswith(s+" "):
                f = {"type":"suspicious_process","line":ln.strip()}
                findings.append(f)
                events.append({"type":"process_alert","data":f})
                if verbose:
                    print("[process_monitor] suspicious:", s, "->", ln.strip())
                break
    return {"findings": findings, "events": events}
