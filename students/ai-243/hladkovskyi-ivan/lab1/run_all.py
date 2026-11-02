"""Запускає всі експерименти по черзі (без паралельних запусків)."""
import subprocess
import sys

STEPS = [
    "task1_reasoning.py",
    "hello_system.py",
    "compare.py",
    "benchmark.py",
    "coldwarm.py",
    "chart.py",
    "sampling.py",
    "quality.py",
]

for s in STEPS:
    print(f"\n######## {s} ########", flush=True)
    code = subprocess.run([sys.executable, s]).returncode
    if code != 0:
        print(f"!!! {s} завершився з помилкою ({code}). Виправте і запустіть його окремо.")
        break
print("\nГотово.")
