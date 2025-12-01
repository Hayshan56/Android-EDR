#!/usr/bin/env python3
"""
modules/anomaly_detector.py
Simple baseline-based anomaly detector.
Provides:
 - gather_metrics(ps_text, net_text, watch_dirs)
 - run_detection(metrics) -> {"anomalies":[...]}
 - run_once(verbose=False)
"""
from utils.logger import info, warn, error
from pathlib import Path
import json
import time
import os

REPORTS = Path("reports")
REPORTS.mkdir(exist_ok=True)

def gather_metrics(ps_text, net_text, watch_dirs):
    """
    Extract simple metrics:
      - process_count
      - network_conn_count (lines in net_text)
      - file_counts for each watch_dir
    """
    metrics = {
        "process_count": 0,
        "network_connections": 0,
        "watch_dir_counts": {},
        "timestamp": int(time.time())
    }
    try:
        metrics["process_count"] = len([l for l in ps_text.splitlines() if l.strip()])
    except Exception:
        metrics["process_count"] = 0
    try:
        metrics["network_connections"] = len([l for l in net_text.splitlines() if l.strip()])
    except Exception:
        metrics["network_connections"] = 0

    for d in watch_dirs or []:
        try:
            count = 0
            for root, dirs, files in os.walk(d):
                count += len(files)
            metrics["watch_dir_counts"][d] = count
        except Exception:
            metrics["watch_dir_counts"][d] = 0
    return metrics

def run_detection(metrics):
    """
    Compare metrics to baseline.json (if present) and return anomalies.
    """
    anomalies = []
    baseline_path = REPORTS / "baseline.json"
    baseline = {}
    try:
        if baseline_path.exists():
            baseline = json.loads(baseline_path.read_text())
    except Exception:
        baseline = {}

    # Simple threshold logic
    proc = metrics.get("process_count", 0)
    netc = metrics.get("network_connections", 0)

    b_proc = baseline.get("average_process_count", None)
    b_net = baseline.get("average_network_connections", None)

    if b_proc is not None:
        if proc > (b_proc * 1.5):
            anomalies.append({"metric":"process_count","value":proc,"baseline":b_proc,"reason":"process spike"})
    if b_net is not None:
        if netc > (b_net * 2):
            anomalies.append({"metric":"network_connections","value":netc,"baseline":b_net,"reason":"network spike"})

    # watch dir changes simple rule
    for d, c in metrics.get("watch_dir_counts", {}).items():
        bcount = baseline.get("average_open_files", None)
        # only report if ratio > 2 compared to baseline open files as rough proxy
        if bcount and c > (bcount * 2):
            anomalies.append({"metric":f"files_in_{d}","value":c,"baseline":bcount,"reason":"file churn"})

    result = {"timestamp": int(time.time()), "anomalies": anomalies}
    # save small report
    try:
        REPORTS.joinpath(f"anomaly_{result['timestamp']}.json").write_text(json.dumps(result, indent=2))
    except Exception:
        pass

    return result

def run_once(ps_text=None, net_text=None, watch_dirs=None, verbose=False):
    info("[anomaly_detector] Running anomaly detector")
    if ps_text is None:
        ps_text = ""
    if net_text is None:
        net_text = ""
    metrics = gather_metrics(ps_text, net_text, watch_dirs or ["/data/data", "/sdcard", "/storage/emulated/0"])
    res = run_detection(metrics)
    if verbose:
        info(f"[anomaly_detector] result: {res}")
    return res
