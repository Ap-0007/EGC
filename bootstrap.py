#!/usr/bin/env python3
import sys
import os
import subprocess
import shutil

def run_command(cmd, desc):
    print(f"[EGC Bootstrap] {desc}...")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[EGC Bootstrap] Error: {e}")
        sys.exit(1)

def validate_environment():
    # 1. Python check
    if sys.version_info < (3, 10):
        print("[EGC Bootstrap] Python 3.10+ required.")
        sys.exit(1)
    
    # 2. Filesystem check
    required_dirs = ['scripts/execution', '.sessions', 'scripts/runtime']
    for d in required_dirs:
        os.makedirs(d, exist_ok=True)
        
    print("[EGC Bootstrap] Environment validated.")

def install_dependencies():
    if shutil.which("pip"):
        run_command([sys.executable, "-m", "pip", "install", "-e", "."], "Installing dependencies")
    else:
        print("[EGC Bootstrap] pip not found. Please install dependencies manually.")

if __name__ == "__main__":
    validate_environment()
    install_dependencies()
    print("[EGC Bootstrap] Installation complete.")
