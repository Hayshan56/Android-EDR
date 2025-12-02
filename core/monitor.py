#!/usr/bin/env python3
"""
core/monitor.py
Central monitoring loop (fixed version).
"""

import time
from core.engine import run_cycle
from core.event_bus import EventBus
from utils.logger import info, warn

class Monitor:

    @staticmethod
    def run_once(verbose=False):
        event_bus = EventBus()

        if verbose:
            info("[monitor] Running single detection cycle")

        result = run_cycle(event_bus, verbose=verbose)

        if verbose:
            info(f"[monitor] Result: {result}")

        return result

    @staticmethod
    def start_loop(interval=8, verbose=False):
        info("[monitor] Continuous monitor started")
        while True:
            Monitor.run_once(verbose=verbose)
            time.sleep(interval)

    @staticmethod
    def run_for(seconds, interval=8, verbose=False):
        info(f"[monitor] Monitor running for {seconds}s")
        end = time.time() + seconds
        while time.time() < end:
            Monitor.run_once(verbose=verbose)
            time.sleep(interval)
