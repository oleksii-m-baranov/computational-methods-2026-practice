"""Частина 1 лаби 5: документи, нарізання, ембединги, перевірка пошуку для всіх нарізань.
Виведення - у консоль і logs/part1_output.txt. Запуск: python run_part1.py"""
import os
import subprocess
import sys

PY = sys.executable
STEPS = [
    ["ollama", "pull", "bge-m3"],
    [PY, "check_cases.py"],
    [PY, "guess_check.py"],
    [PY, "show_chunks.py", "data/docs/d01.txt", "fixed", "200", "0"],
    [PY, "show_chunks.py", "data/docs/d01.txt", "fixed", "500", "100"],
    [PY, "show_chunks.py", "data/docs/d01.txt", "paragraphs", "800"],
    [PY, "embed_check.py"],
    [PY, "build_index.py"],
    [PY, "check_retrieval.py"],
    [PY, "scores_all.py"],
]
os.makedirs("logs", exist_ok=True)
os.makedirs("results", exist_ok=True)
env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
with open("logs/part1_output.txt", "w", encoding="utf-8") as out:
    for i, step in enumerate(STEPS, 1):
        title = " ".join("python" if s == PY else s for s in step)
        line = f"\n##### [{i}/{len(STEPS)}] {title}\n"
        print(line, end="", flush=True)
        out.write(line)
        proc = subprocess.run(step, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
        text = proc.stdout + (proc.stderr if proc.returncode else "")
        print(text, end="", flush=True)
        out.write(text)
        out.flush()
        if proc.returncode != 0:
            print(f"\n!!! Крок завершився з кодом {proc.returncode}. Зупиняюсь.")
            sys.exit(proc.returncode)
    print("\n##### ГОТОВО. Виведення - у logs/part1_output.txt")
