#!/usr/bin/env bash
set -e

echo "[*] Android-EDR installer (Termux)"

# Update packages
if command -v pkg >/dev/null 2>&1; then
    pkg update -y
    pkg upgrade -y
    PKG_INSTALL="pkg install -y"
else
    echo "[!] Warning: 'pkg' not found. Try your distro package manager."
    PKG_INSTALL="apt-get install -y"
fi

# Essentials for Termux
$PKG_INSTALL python git curl nano openssh clang

# pip (Termux python includes pip usually)
if ! command -v pip >/dev/null 2>&1; then
    echo "[*] Installing pip..."
    $PKG_INSTALL python-pip || true
fi

# Install Python deps from requirements.txt
if [ -f requirements.txt ]; then
    echo "[*] Installing Python requirements..."
    pip install --no-cache-dir -r requirements.txt
else
    echo "[!] requirements.txt not found, skipping pip install."
fi

# Create reports/logs directories
mkdir -p reports logs config

# Install launcher to PREFIX/bin
PREFIX=${PREFIX:-/data/data/com.termux/files/usr}
BIN_DIR="$PREFIX/bin"
mkdir -p "$BIN_DIR"

# If you want the launcher to be core/main.py or a root script:
# prefer if core/main.py exists
if [ -f core/main.py ]; then
    cp core/main.py "$BIN_DIR/android-edr"
    chmod +x "$BIN_DIR/android-edr"
    echo "[*] Launcher installed to $BIN_DIR/android-edr"
else
    echo "[!] core/main.py not found. You can run: python3 core/main.py"
fi

echo "[*] Install complete. Run: android-edr --help  OR python3 core/main.py --help"
