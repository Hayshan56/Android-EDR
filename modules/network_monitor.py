#!/usr/bin/env python3
"""
modules/network_monitor.py
Collects active network sockets and tries to match against simple rules.
Returns dict with findings and optional events.
"""
import subprocess
import json
import socket
import time

DEFAULT_RULES = [
    # sample suspicious remote IP ranges (placeholder)
    "185.", "45.", "103."
]

def _run_cmd(cmd):
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True)
        return out
    except Exception:
        return ""

def _parse_ss_output(txt):
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    entries = []
    for ln in lines[1:]:
        parts = ln.split()
        # best-effort parse: local remote state pid
        try:
            local = parts[3]
            remote = parts[4]
            state = parts[1] if len(parts) > 1 else ""
            entries.append({"raw": ln, "local": local, "remote": remote, "state": state})
        except Exception:
            entries.append({"raw": ln})
    return entries

def run_once(verbose=False):
    findings = []
    events = []
    ts = int(time.time())

    out = _run_cmd(["ss","-tunap"]) or _run_cmd(["netstat","-tunap"])
    entries = _parse_ss_output(out)
    for e in entries:
        remote = e.get("remote","")
        # quick check for suspicious remote prefixes
        for p in DEFAULT_RULES:
            if remote and p in remote:
                f = {"type":"suspicious_connection","remote":remote,"raw":e.get("raw")}
                findings.append(f)
                events.append({"type":"network_alert","data":f})
                if verbose:
                    print("[network_monitor] flagged", remote)
                break

    return {"findings": findings, "events": events}
