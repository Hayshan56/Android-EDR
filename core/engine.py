#!/usr/bin/env python3
"""
core/engine.py
Writes reports into a GLOBAL safe directory:
~/Android-EDR-Reports/
"""

import importlib
import json
import os
import time
from pathlib import Path

# GLOBAL report directory (outside project)
REPORTS_DIR = Path.home() / "Android-EDR-Reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

def _get_logger():
    try:
        mod = importlib.import_module("utils.logger")
        return getattr(mod, "get_logger", lambda name: mod)()
    except Exception:
        class SimpleLogger:
            def info(self, *a, **k): print("[*]", *a)
            def warn(self, *a, **k): print("[!]", *a)
            def error(self, *a, **k): print("[ERROR]", *a)
        return SimpleLogger()

logger = _get_logger()

def safe_import_module(name):
    try:
        return importlib.import_module(name)
    except Exception:
        logger.warn(f"Module not available: {name}")
        return None

MODULES = [
    "modules.process_monitor",
    "modules.network_monitor",
    "modules.file_monitor",
    "modules.persistence_detector",
    "modules.behavior_engine",
    "modules.anomaly_detector",
    "modules.apk_analyzer",
]

def run_cycle(event_bus, verbose=False):
    ts = int(time.time())
    logger.info("Engine: starting detection cycle", ts)
    findings = []

    for mname in MODULES:
        m = safe_import_module(mname)
        if not m:
            continue
        fn = getattr(m, "run_once", None) or getattr(m, "scan", None) or getattr(m, "run", None)
        if not callable(fn):
            logger.info(f"{mname} has no run_once/scan/run - skipping")
            continue

        try:
            res = fn(verbose=verbose) if "verbose" in fn.__code__.co_varnames else fn()
            if isinstance(res, dict):
                if res.get("findings"):
                    findings.extend(res.get("findings"))
                if res.get("events"):
                    for e in res.get("events"):
                        event_bus.emit(e.get("type","unknown"), e.get("data",{}))
            elif isinstance(res, list):
                findings.extend(res)
            elif res:
                findings.append({"module": mname, "result": str(res)})
        except Exception as e:
            logger.error(f"Error running {mname}: {e}")

    correlator = safe_import_module("modules.correlator") or safe_import_module("modules.behavior_engine_v2")
    if correlator:
        try:
            fn = getattr(correlator, "correlate", None) or getattr(correlator, "run_correlation", None)
            if callable(fn):
                corr = fn(findings=findings, verbose=verbose)
                if isinstance(corr, dict) and corr.get("findings"):
                    findings.extend(corr.get("findings"))
        except Exception as e:
            logger.warn("Correlator error: " + str(e))

    events = []
    try:
        events = event_bus.drain()
    except Exception:
        logger.warn("EventBus drain failed")

    summary = {
        "timestamp": ts,
        "summary_count": len(findings),
        "findings": findings,
        "events": events
    }

    if summary["summary_count"] or events:
        fname = REPORTS_DIR / f"report_{ts}.json"
        try:
            with open(fname, "w", encoding='utf-8') as fh:
                json.dump(summary, fh, indent=2, ensure_ascii=False)
            logger.info(f"Saved report: {fname}")
        except Exception as e:
            logger.error("Failed to save report: " + str(e))
    else:
        logger.info("No findings this cycle")

    return summary
