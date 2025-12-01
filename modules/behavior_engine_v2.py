#!/usr/bin/env python3
"""
modules/behavior_engine_v2.py
Improved correlator:
 - accepts findings list
 - groups by type
 - assigns MITRE-like tags (local mapping)
 - returns aggregated findings for engine to persist
"""
import time
from collections import defaultdict

TYPE_TO_MITRE = {
    "suspicious_connection": "T1071",
    "suspicious_process": "T1059",
    "suspicious_file": "T1090",
    "persistence_file": "T1547",
    "root_indicator": "T1068",
}

def correlate(findings=None, verbose=False):
    findings = findings or []
    by_type = defaultdict(list)
    for f in findings:
        by_type[f.get("type","unknown")].append(f)

    aggregated = []
    for t, items in by_type.items():
        mitre = TYPE_TO_MITRE.get(t, "T0000")
        agg = {"type":"aggregated","category":t,"count":len(items),"mitre":mitre}
        aggregated.append(agg)
        if verbose:
            print("[behavior_v2] aggregated", agg)
    return {"findings": aggregated}
