#!/usr/bin/env python3
"""
utils/logger.py
Simple colored logger with levels.
"""
import sys
import time

COLOR = {
    "RED": "\033[91m",
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "BLUE": "\033[94m",
    "END": "\033[0m",
}

def timestamp():
    return time.strftime("%Y-%m-%d %H:%M:%S")

def log(msg="", level="INFO"):
    color = COLOR["GREEN"]
    if level == "WARN":
        color = COLOR["YELLOW"]
    elif level == "ERROR":
        color = COLOR["RED"]
    elif level == "DEBUG":
        color = COLOR["BLUE"]

    sys.stdout.write(f"{color}[{timestamp()}] [{level}] {msg}{COLOR['END']}\n")

def info(msg): log(msg, "INFO")
def warn(msg): log(msg, "WARN")
def error(msg): log(msg, "ERROR")
def debug(msg): log(msg, "DEBUG")
