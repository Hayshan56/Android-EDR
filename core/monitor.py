#!/usr/bin/env python3
"""
core/monitor.py
High-level monitor that repeatedly calls engine.run_cycle on a schedule.
Exposes a Monitor class used by core/main.py or by the CLI.
"""
import time
import threading
import importlib
from .event_bus import EventBus
from .engine import run_cycle
from pathlib import Path

# safe logger fallback
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

class Monitor:
    def __init__(self, interval=8, verbose=False):
        self.interval = max(1, int(interval))
        self.verbose = verbose
        self.event_bus = EventBus()
        self._stop = threading.Event()
        self._thread = None

    def _loop(self):
        logger.info(f"Monitor loop started (interval={self.interval}s)")
        while not self._stop.is_set():
            try:
                run_cycle(self.event_bus, verbose=self.verbose)
            except Exception as e:
                logger.error("Engine failure: " + str(e))
            # sleep with stop-check
            for _ in range(self.interval):
                if self._stop.is_set():
                    break
                time.sleep(1)
        logger.info("Monitor loop exiting")

    def start(self):
        if self._thread and self._thread.is_alive():
            logger.info("Monitor already running")
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Monitor stopped")

    def run_once(self):
        return run_cycle(self.event_bus, verbose=self.verbose)
