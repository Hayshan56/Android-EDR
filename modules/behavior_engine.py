#!/usr/bin/env python3
"""
modules/behavior_engine.py
Simple rule-based correlator that consumes findings list and scores them.
This is version 1 behavior engine (keeps compatibility).
"""
import time

RULE_WEIGHTS = {
    "suspicious_connection": 5,
    "suspicious_process": 6,
    "suspicious_file": 4,
    "persistence_file": 7,
    "root_indicator": 9,
    "anomaly": 3
}

def run_once(verbose=False):
    # legacy module: returns empty (engine.run_cycle will call v2 correlator)
    return {"findings": [], "events":[]}

def run_correlation(findings=None, verbose=False):
    """
    Accept list of findings from modules and return calculated correlated results.
    """
    if findings is None:
        findings = []

    correlated = []
    score = 0
    for f in findings:
        t = f.get("type")
        w = RULE_WEIGHTS.get(t, 1)
        score += w
        correlated.append({"type":"correlated","src":f,"weight":w})

    result = {"findings": correlated, "score": score, "timestamp": int(time.time())}
    if verbose:
        print("[behavior_engine] correlated score:", score)
    return {"findings": correlated}
