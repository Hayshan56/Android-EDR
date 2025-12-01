#!/usr/bin/env python3
"""
modules/system_behavior.py
Simple heuristic module that derives 'behavior' signals from other quick checks.
This returns a heuristic score and events.
"""
import os
import time

def run_once(verbose=False):
    findings = []
    events = []
    # heuristic: if /data/local/tmp contains executables, treat as suspicious
    try:
        for root, dirs, files in os.walk("/data/local/tmp"):
            for fn in files:
                if fn.endswith(".sh") or fn.endswith(".bin") or fn.endswith(".apk"):
                    f = {"type":"suspicious_local_file","path": os.path.join(root, fn)}
                    findings.append(f)
                    events.append({"type":"behavior_hint","data": f})
                    if verbose:
                        print("[system_behavior] heuristic hit", f)
            # only top-level for speed
            break
    except Exception:
        pass
    return {"findings": findings, "events": events}
