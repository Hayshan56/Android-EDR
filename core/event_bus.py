#!/usr/bin/env python3
"""
core/event_bus.py
Simple in-memory event bus used by the engine and modules.
Events are small dicts: {"type": "...", "data": {...}, "ts": 1234567890}
"""
import time
import threading

class EventBus:
    def __init__(self):
        self._lock = threading.Lock()
        self._events = []

    def emit(self, event_type, data):
        evt = {
            "type": event_type,
            "data": data,
            "ts": int(time.time())
        }
        with self._lock:
            self._events.append(evt)

    def drain(self):
        """Return and clear current events (thread-safe)."""
        with self._lock:
            evts = list(self._events)
            self._events.clear()
        return evts

    def peek(self):
        with self._lock:
            return list(self._events)
