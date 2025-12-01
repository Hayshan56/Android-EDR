#!/usr/bin/env python3
"""
core/scheduler.py
A tiny scheduler wrapper around Monitor to support:
 - one-shot runs
 - continuous monitoring (same as monitor.start)
 - scheduling via cron-like delay (simple)
This is optional helper used by main.
"""
import time
from threading import Thread
from .monitor import Monitor

class Scheduler:
    def __init__(self, interval=8, verbose=False):
        self.monitor = Monitor(interval=interval, verbose=verbose)

    def start_background(self):
        self.monitor.start()

    def stop(self):
        self.monitor.stop()

    def run_once(self):
        return self.monitor.run_once()

    def run_for(self, seconds):
        self.monitor.start()
        time.sleep(seconds)
        self.monitor.stop()
