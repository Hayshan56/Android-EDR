#!/usr/bin/env python3
"""
modules/persistence_detector.py
Looks for common Android persistence indicators (init.d, cron-like files, suspicious boot receivers)
Non-exhaustive; meant for Termux environment detection.
"""
from pathlib import Path

CHECK_PATHS = [
    "/system/etc/init.d",
    "/etc/init.d",
    "/data/local/tmp",
    "/data/system/packages.list"
]

def run_once(verbose=False):
    findings = []
    events = []
    for p in CHECK_PATHS:
        try:
            pp = Path(p)
            if pp.exists():
                for child in pp.iterdir():
                    if child.is_file():
                        f = {"type":"persistence_file","path":str(child)}
                        findings.append(f)
                        events.append({"type":"persistence", "data": f})
                        if verbose:
                            print("[persistence_detector] found", child)
        except Exception:
            continue
    return {"findings": findings, "events": events}
