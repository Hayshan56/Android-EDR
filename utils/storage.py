#!/usr/bin/env python3
"""
utils/storage.py
Handles persistent storage of scan results, logs, and correlations.
Stores everything in JSON under /logs directory.
"""
import json
from pathlib import Path
import time

BASE = Path("logs")
BASE.mkdir(exist_ok=True)

def _write(file, data):
    try:
        file.write_text(json.dumps(data, indent=2))
    except Exception:
        pass

def save_scan_result(result, filename=None):
    ts = int(time.time())
    name = filename or f"scan_{ts}.json"
    p = BASE / name
    _write(p, result)
    return str(p)

def save_events(events):
    ts = int(time.time())
    p = BASE / f"events_{ts}.json"
    _write(p, events)
    return str(p)

def save_correlation(data):
    ts = int(time.time())
    p = BASE / f"correlation_{ts}.json"
    _write(p, data)
    return str(p)

def list_logs():
    return [str(x) for x in BASE.glob("*.json")]
