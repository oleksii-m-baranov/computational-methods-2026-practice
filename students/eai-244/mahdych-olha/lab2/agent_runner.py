"""Один прогін п'яти задач. Наявні результати не перезаписуються."""
import json
import sys
import shutil
import platform
from datetime import datetime
from pathlib import Path
from importlib.metadata import version

ROOT = Path(__file__).resolve().parent
if Path.cwd().resolve() != ROOT:
    sys.exit("Запускайте програму з папки lab2-mahdych-olha.")
if any((ROOT / name).exists() for name in ("lab2.log", "run_results.json", "log2.lab")):
    sys.exit("Результати вже є. Не запускайте повторно: надішліть lab2.log і run_results.json для перевірки.")

import config
from agent import run_agent, logger

tasks = json.loads((ROOT / "tasks.json").read_text(encoding="utf-8"))
results = {"started_at": datetime.now().astimezone().isoformat(),
           "model": config.MODEL, "temperature": config.TEMPERATURE,
           "max_steps": config.MAX_STEPS, "python": platform.python_version(),
           "openai": version("openai"), "tasks": []}

def save():
    (ROOT / "run_results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

logger.info(f"МОДЕЛЬ: {config.MODEL}; temperature={config.TEMPERATURE}; MAX_STEPS={config.MAX_STEPS}")
try:
    for i, task in enumerate(tasks, 1):
        logger.info(f"\n=== {task['id']} | очікується: {task['expected']}")
        print(f"Задача {i}/5: {task['id']}", flush=True)
        record = {**task, "steps": [], "answer": None, "error": None}
        results["tasks"].append(record)
        try:
            record["answer"] = run_agent(task["question"], record["steps"])
        except Exception as exc:
            record["error"] = f"{type(exc).__name__}: {exc}"
            logger.exception("ПОМИЛКА ЗАПУСКУ")
            save()
            raise
        save()
    results["finished_at"] = datetime.now().astimezone().isoformat()
    logger.info(f"Оброблено задач: {len(tasks)}. Лог: lab2.log")
finally:
    save()
    for handler in logger.handlers:
        handler.flush()
    # Наприкінці методички зазначено log2.lab, у коді — lab2.log.
    # Обидва файли містять один і той самий фактичний лог.
    if (ROOT / "lab2.log").exists():
        shutil.copyfile(ROOT / "lab2.log", ROOT / "log2.lab")
print("ГОТОВО: lab2.log, log2.lab, run_results.json", flush=True)
