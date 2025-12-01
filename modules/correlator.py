#!/usr/bin/env python3
"""
modules/correlator.py
Lightweight correlator: consumes findings and groups related alerts.
"""
from utils.logger import info, warn, error
from pathlib import Path
import json
import time

REPORTS = Path("reports")

def correlate(findings_list):
    """
    findings_list: list of dicts (each dict is a module's findings)
    Return: correlation summary dict
    """
    summary = {
        "timestamp": int(time.time()),
        "total_findings": 0,
        "by_category": {},
        "correlated_groups": []
    }

    # simple aggregation
    for f in findings_list:
        if not isinstance(f, dict):
            continue
        for k, v in f.items():
            # assume v may be list of findings
            if isinstance(v, list):
                for item in v:
                    cat = item.get("type", "unknown")
                    summary["total_findings"] += 1
                    summary["by_category"].setdefault(cat, 0)
                    summary["by_category"][cat] += 1
                    # naive grouping: if same path or process, put into groups
                    key = item.get("path") or item.get("process") or item.get("name")
                    if key:
                        summary["correlated_groups"].append({
                            "key": key,
                            "item": item
                        })
    return summary

def run_and_save(findings_list, name=None):
    s = correlate(findings_list)
    fname = name or f"correlation_{s['timestamp']}.json"
    path = REPORTS / fname
    try:
        path.write_text(json.dumps(s, indent=2))
        info(f"[correlator] Saved correlation: {path}")
    except Exception as e:
        error(f"[correlator] Failed save: {e}")
    return s
