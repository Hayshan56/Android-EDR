#!/usr/bin/env python3
"""
utils/helpers.py
General helper functions used across modules and engine.
"""
import subprocess
import os
from pathlib import Path

def run_cmd(cmd, decode=True):
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
        return out.decode() if decode else out
    except Exception:
        return ""

def safe_read(path):
    try:
        with open(path, "r", errors="ignore") as f:
            return f.read()
    except Exception:
        return ""

def find_files(root, pattern=None):
    results = []
    p = Path(root)
    if not p.exists():
        return results
    for child in p.rglob("*"):
        if child.is_file():
            if pattern:
                if pattern.lower() in child.name.lower():
                    results.append(str(child))
            else:
                results.append(str(child))
    return results

def is_executable(path):
    try:
        return os.access(path, os.X_OK)
    except Exception:
        return False
