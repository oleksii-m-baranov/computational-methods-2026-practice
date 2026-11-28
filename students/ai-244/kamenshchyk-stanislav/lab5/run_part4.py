"""Частина 4 лаби 5: вимірювання після виправлення старої назви search_service в описі price_info і в checks.py.
Результати етапу 3 (лише виправлення порожньої відповіді) переносяться в logs/fix1/ і results/rag_fix1.csv.
Виведення - у консоль і logs/part4_output.txt. Запуск: python run_part4.py"""
import glob
import os
import shutil
import subprocess
import sys

PY = sys.executable
STEPS = [
    "ARCHIVE",
    [PY, "ask.py", "D1"],
    [PY, "measure_rag.py"],
    [PY, "rag_report.py"],
    "RESET_LAB5_LOG",
    [PY, "agent_runner.py"],
    "RENAME_RUN_RAG",
]
env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
os.makedirs("logs", exist_ok=True)

with open("logs/part4_output.txt", "w", encoding="utf-8") as out:
    def write(text):
        print(text, end="", flush=True)
        out.write(text)
        out.flush()

    for i, step in enumerate(STEPS, 1):
        if step == "ARCHIVE":
            dest = "logs/fix1"
            if not os.path.exists(dest):
                os.makedirs(dest)
                for path in glob.glob("logs/rag_*.log") + ["logs/run_rag.log", "logs/ask_lab5.log"]:
                    if os.path.exists(path):
                        shutil.move(path, dest)
                if os.path.exists("results/rag.csv"):
                    shutil.move("results/rag.csv", "results/rag_fix1.csv")
            write(f"\n##### [{i}/{len(STEPS)}] результати етапу 3 -> logs/fix1/, results/rag_fix1.csv\n")
            continue
        if step == "RESET_LAB5_LOG":
            if os.path.exists("logs/lab5.log"):
                os.replace("logs/lab5.log", "logs/ask_lab5.log")
            write(f"\n##### [{i}/{len(STEPS)}] logs/lab5.log (прогони ask.py) -> logs/ask_lab5.log\n")
            continue
        if step == "RENAME_RUN_RAG":
            os.replace("logs/lab5.log", "logs/run_rag.log")
            write(f"\n##### [{i}/{len(STEPS)}] logs/lab5.log -> logs/run_rag.log\n")
            continue
        write(f"\n##### [{i}/{len(STEPS)}] " + " ".join("python" if s == PY else s for s in step) + "\n")
        proc = subprocess.Popen(step, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                env=env, text=True, encoding="utf-8", errors="replace")
        for line in proc.stdout:
            write(line)
        proc.wait()
        if proc.returncode != 0:
            write(f"\n!!! Крок завершився з кодом {proc.returncode}. Зупиняюсь.\n")
            sys.exit(proc.returncode)
    write("\n##### ГОТОВО. Виведення - у logs/part4_output.txt\n")
