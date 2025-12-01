#!/usr/bin/env python3
"""
modules/signatures.py
Simple signature loader for malware_signatures.
Loads config/signatures.json if it exists.
"""
import json
from pathlib import Path

DEFAULT = [
    {"id":"MAL-001","pattern":"dropbear"},
    {"id":"MAL-002","pattern":"backdoor"},
]

def load_signatures():
    cfg = Path("config/signatures.json")
    if cfg.exists():
        try:
            return json.loads(cfg.read_text())
        except Exception:
            return DEFAULT
    return DEFAULT

if __name__ == "__main__":
    import pprint
    pprint.pprint(load_signatures())
