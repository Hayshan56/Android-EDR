#!/usr/bin/env python3
"""
utils/crypto.py
Lightweight hashing utilities for integrity checks.
"""
import hashlib

def sha256_file(path):
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None

def sha256_str(s: str):
    try:
        return hashlib.sha256(s.encode()).hexdigest()
    except Exception:
        return None

def md5_file(path):
    try:
        h = hashlib.md5()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None
