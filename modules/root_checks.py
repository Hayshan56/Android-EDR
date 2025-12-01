#!/usr/bin/env python3
"""
modules/root_checks.py
Lightweight checks for root indicators (su binary, magisk files).
"""
from pathlib import Path

ROOT_INDICATORS = [
    "/system/xbin/su",
    "/system/bin/su",
    "/sbin/su",
    "/data/adb/magisk",
    "/data/adb/magisk.db"
]

def run_once(verbose=False):
    findings = []
    events = []
    for p in ROOT_INDICATORS:
        try:
            pp = Path(p)
            if pp.exists():
                f = {"type":"root_indicator","path":p}
                findings.append(f)
                events.append({"type":"root_detected","data":f})
                if verbose:
                    print("[root_checks] indicator found", p)
        except Exception:
            continue
    return {"findings": findings, "events": events}
