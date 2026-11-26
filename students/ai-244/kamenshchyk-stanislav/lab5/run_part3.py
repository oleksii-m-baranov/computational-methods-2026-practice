"""Частина 3 лаби 5: повторне вимірювання після виправлення check_response (порожня відповідь).
База ЛР4 для табл. 7 (baseline_lab4.py) уже прогнана старим агентом: logs/run_lab4_tasks.log.
Перші результати зберігаються в logs/before_fix/ і results/rag_before_fix.csv.
Виведення - у консоль і logs/part3_output.txt. Запуск: python run_part3.py"""
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

with open("logs/part3_output.txt", "w", encoding="utf-8") as out:
    def write(text):
        print(text, end="", flush=True)
        out.write(text)
        out.flush()

    for i, step in enumerate(STEPS, 1):
        if step == "ARCHIVE":
            dest = "logs/before_fix"
            if not os.path.exists(dest):
                os.makedirs(dest)
                for path in glob.glob("logs/rag_*.log") + ["logs/run_rag.log", "logs/ask_lab5.log"]:
                    if os.path.exists(path):
                        shutil.move(path, dest)
                if os.path.exists("results/rag.csv"):
                    shutil.move("results/rag.csv", "results/rag_before_fix.csv")
            write(f"\n##### [{i}/{len(STEPS)}] перші результати -> logs/before_fix/, results/rag_before_fix.csv\n")
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
    write("\n##### ГОТОВО. Виведення - у logs/part3_output.txt\n")
