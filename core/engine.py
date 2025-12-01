#!/usr/bin/env python3
"""
core/engine.py
Orchestrates one detection cycle:
 - collects snapshots from modules
 - runs behavior / signature correlation
 - writes reports (to reports/ directory)
This file is intentionally defensive: missing modules or utils won't break imports.
"""
import importlib
import json
import os
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
REPORTS_DIR = BASE_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# safe logger fallback (utils.logger added later)
def _get_logger():
    try:
        mod = importlib.import_module("utils.logger")
        return getattr(mod, "get_logger", lambda name: mod)()  # if function exists
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

# Module names expected (will be present in modules/)
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
    """
    Run a single detection cycle:
    - invoke each module's 'run_once' or 'scan' or 'run' entrypoint (defensive)
    - collect module outputs as events on the bus
    - call correlator (if present)
    - persist a summary report if any findings exist
    """
    ts = int(time.time())
    logger.info("Engine: starting detection cycle", ts)
    findings = []

    for mname in MODULES:
        m = safe_import_module(mname)
        if not m:
            continue
        # find a callable entrypoint
        fn = getattr(m, "run_once", None) or getattr(m, "scan", None) or getattr(m, "run", None)
        if not callable(fn):
            logger.info(f"{mname} has no run_once/scan/run - skipping")
            continue
        try:
            res = fn(verbose=verbose) if "verbose" in fn.__code__.co_varnames else fn()
            # module may emit events to shared event_bus or return findings directly
            if isinstance(res, dict):
                if res.get("findings"):
                    findings.extend(res.get("findings"))
                # modules may also return 'events'
                if res.get("events"):
                    for e in res.get("events"):
                        event_bus.emit(e.get("type","unknown"), e.get("data",{}))
            elif isinstance(res, list):
                findings.extend(res)
            elif res:
                # generic non-empty return
                findings.append({"module": mname, "result": str(res)})
        except Exception as e:
            logger.error(f"Error running {mname}: {e}")

    # run correlator if available
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

    # drain bus for module-emitted events
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

    # only save if something interesting
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
