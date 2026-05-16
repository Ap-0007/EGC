import sys
import os
import shutil

def run_doctor():
    print("[EGC Doctor] Starting runtime diagnostic...")
    
    # 1. Python Check
    print(f"[EGC Doctor] Python: {sys.version.split()[0]} - {'OK' if sys.version_info >= (3, 10) else 'FAIL'}")
    
    # 2. Node Check (Auxiliary)
    node_path = shutil.which("node")
    print(f"[EGC Doctor] Node.js: {node_path if node_path else 'Not found (Optional)'}")
    
    # 3. Filesystem/Sandbox
    dirs = ['.sessions', 'scripts/execution', 'scripts/runtime']
    for d in dirs:
        print(f"[EGC Doctor] Dir {d}: {'Exists' if os.path.exists(d) else 'Missing'}")

    # 4. Dependency Check (pip)
    pip_path = shutil.which("pip")
    print(f"[EGC Doctor] Pip: {pip_path if pip_path else 'Not found'}")
    
    print("[EGC Doctor] Diagnostic complete.")

if __name__ == "__main__":
    run_doctor()
