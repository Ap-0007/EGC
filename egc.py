#!/usr/bin/env python3
import sys
import asyncio
import os
from scripts.runtime.doctor_core import run_doctor
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'scripts')))
from orchestration.orchestrator import ExecutionOrchestrator

def main():
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "doctor":
            run_doctor()
        elif cmd == "start":
            asyncio.run(start_runtime())
        else:
            print(f"Unknown command: {cmd}")
    else:
        asyncio.run(start_runtime())

async def start_runtime():
    print("Starting EGC Runtime...")
    orch = ExecutionOrchestrator(os.getcwd())
    print("Runtime Ready.")

start = main

if __name__ == "__main__":
    main()
