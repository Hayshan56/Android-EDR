#!/usr/bin/env python3
"""
modules/network_rules.py
Simple loader for network rule patterns used by network_monitor.
Expect config/network_rules.json or internal defaults.
"""
import json
from pathlib import Path

DEFAULT = [
    "185.",
    "45.",
    "103."
]

def load_rules():
    cfg = Path("config/network_rules.json")
    if cfg.exists():
        try:
            return json.loads(cfg.read_text())
        except Exception:
            return DEFAULT
    return DEFAULT

if __name__ == "__main__":
    print(load_rules())
