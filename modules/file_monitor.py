#!/usr/bin/env python3
"""
modules/file_monitor.py
Performs lightweight checks for suspicious files & common persistence locations.
This is a static snapshot scan for 'interesting' files (no inotify).
"""
from pathlib import Path
import time

COMMON_PATHS = [
    "/data/local/tmp",
    "/sdcard",
    "/data/data"
]

COMMON_SUSPICIOUS = [
    "su",
    "busybox",
    "backdoor",
    "payload",
    "dropbear"
]

def _scan_paths():
    found = []
    for base in COMMON_PATHS:
        p = Path(base)
        if not p.exists():
            continue
        try:
            for child in p.rglob("*"):
                name = child.name.lower()
                for s in COMMON_SUSPICIOUS:
                    if s in name:
                        found.append({"path": str(child), "match": s})
        except Exception:
            continue
    return found

def run_once(verbose=False):
    findings = []
    events = []
    hits = _scan_paths()
    for h in hits:
        f = {"type":"suspicious_file","path":h["path"], "match": h["match"]}
        findings.append(f)
        events.append({"type":"file_alert","data":f})
        if verbose:
            print("[file_monitor] found", f)
    return {"findings": findings, "events": events}
