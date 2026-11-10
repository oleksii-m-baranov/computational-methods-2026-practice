import json
import sys
from pathlib import Path
from datetime import datetime
from importlib.metadata import version

ROOT = Path(__file__).resolve().parent
if Path.cwd().resolve() != ROOT:
    sys.exit("Run from lab3-mahdych-olha.")
if any((ROOT / n).exists() for n in ("lab3_checks.log", "lab3_checks_results.json")):
    sys.exit("CHECKS_RESULTS_EXIST. Do not overwrite results.")
if not (ROOT / "lab3_baseline.log").exists():
    sys.exit("BASELINE_MISSING. Stop and contact the assistant.")

import config
from langfuse import get_client, propagate_attributes
from agent import run_agent, logger

tasks = json.loads((ROOT / "tasks.json").read_text(encoding="utf-8"))
results = {"run_tag": config.RUN_TAG, "model": config.MODEL, "temperature": config.TEMPERATURE, "max_steps": config.MAX_STEPS, "max_retries": config.MAX_RETRIES, "langfuse": version("langfuse"), "started_at": datetime.now().astimezone().isoformat(), "tasks": []}
def save():
    (ROOT / "lab3_checks_results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
try:
    for i, task in enumerate(tasks, 1):
        print(f"TASK {i}/5: {task['id']}", flush=True)
        logger.info(f"\n=== {task['id']} | очікується: {task['expected']}")
        record = {**task, "steps": [], "answer": None, "error": None}
        results["tasks"].append(record)
        try:
            with propagate_attributes(trace_name=f"checks-{task['id']}", tags=["checks"]):
                record["answer"] = run_agent(task["question"], record["steps"])
        except Exception as exc:
            record["error"] = type(exc).__name__ + ": " + str(exc)
            raise
        finally:
            save()
    results["finished_at"] = datetime.now().astimezone().isoformat()
finally:
    save()
    get_client().flush()
    for handler in logger.handlers:
        handler.flush()
print("DONE: lab3_checks.log, lab3_checks_results.json", flush=True)
