"""Частина 2 лаби 5: остаточний індекс, поріг, інструмент, агент з трьома описами, звичайні задачі.
Виведення - у консоль і logs/part2_output.txt. Запуск: python run_part2.py"""
import os
import subprocess
import sys

PY = sys.executable
STEPS = [
    [PY, "build_index.py"],
    [PY, "check_retrieval.py", "scores"],
    [PY, "try_tool.py", "D1"],
    [PY, "try_tool.py", "N1"],
    [PY, "ask.py", "D1"],
    [PY, "measure_rag.py", "B", "1"],
    [PY, "measure_rag.py"],
    [PY, "rag_report.py"],
    "RESET_LAB5_LOG",
    [PY, "agent_runner.py"],
    "RENAME_RUN_RAG",
]
os.makedirs("logs", exist_ok=True)
env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
with open("logs/part2_output.txt", "w", encoding="utf-8") as out:
    def write(text):
        print(text, end="", flush=True)
        out.write(text)
        out.flush()

    for i, step in enumerate(STEPS, 1):
        if step == "RESET_LAB5_LOG":        # крок 9: у run_rag.log мають бути лише п'ять задач
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
    write("\n##### ГОТОВО. Виведення - у logs/part2_output.txt\n")
