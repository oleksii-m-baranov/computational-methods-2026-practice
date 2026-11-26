"""Прогін агента на всіх питаннях із tasks.json.

python agent_runner.py baseline   - агент з ЛР2 без змін (+ трасування)
python agent_runner.py checks     - агент з перевірками
python agent_runner.py provoke provoke_tasks.json - питання, що провокують помилки (крок 9)
"""
import json
import os
import sys
import time

if len(sys.argv) > 1:
    os.environ["RUN_TAG"] = sys.argv[1]       # мітку треба задати до імпорту config

import config                                  # noqa: E402
from langfuse import get_client, propagate_attributes  # noqa: E402
from utils.lab_logger import custom_logger     # noqa: E402

if config.RUN_TAG == "baseline":
    import baseline.agent as agent_module
else:
    import agent as agent_module

logger = custom_logger(config.LAB_LOGFILE_NAME)

TASKS_FILE = sys.argv[2] if len(sys.argv) > 2 else "tasks.json"

with open(TASKS_FILE, encoding="utf-8") as f:
    tasks = json.load(f)

stats = []
for task in tasks:
    logger.info(f"\n### {task['id']} | очікується: {task['expected']}")
    t0 = time.perf_counter()
    # назва траси (наприклад, baseline-Z1) і мітка прогону
    with propagate_attributes(trace_name=f"{config.RUN_TAG}-{task['id']}",
                              tags=[config.RUN_TAG]):
        answer = agent_module.run_agent(task["question"])
    stats.append({
        "id": task["id"],
        "model_calls": agent_module.STATS["model_calls"],
        "tokens": agent_module.STATS["tokens"],
        "time_s": round(time.perf_counter() - t0, 2),
        "answer": answer,
    })

get_client().flush()                           # дочекатися відправки подій

os.makedirs("results", exist_ok=True)
with open(f"results/{config.RUN_TAG}_stats.json", "w", encoding="utf-8") as f:
    json.dump(stats, f, ensure_ascii=False, indent=2)

logger.info(f"\nОброблено задач: {len(tasks)}. Лог: logs/{config.LAB_LOGFILE_NAME}.log")
