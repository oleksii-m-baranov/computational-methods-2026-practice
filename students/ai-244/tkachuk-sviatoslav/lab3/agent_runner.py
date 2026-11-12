"""Запуск контрольних задач у режимах baseline і checks."""
import argparse
import json
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
from utils.lab_logger import custom_logger
import config


def main():
    parser = argparse.ArgumentParser(description="ЛР №3, baseline / checks")
    parser.add_argument("--run", required=True, choices=["baseline", "checks"])
    opts = parser.parse_args()
    os.chdir(HERE)
    config.RUN_TAG = opts.run
    logger = custom_logger(config.LAB_LOGFILE_NAME, overwrite=True)
    from agent import run_agent
    from langfuse import get_client, propagate_attributes
    with (HERE / "tasks.json").open(encoding="utf-8") as f:
        tasks = json.load(f)
    logger.info(f"РЕЖИМ: {opts.run} | модель: {config.MODEL} | temperature={config.TEMPERATURE}")
    public = os.getenv("LANGFUSE_PUBLIC_KEY", "")
    secret = os.getenv("LANGFUSE_SECRET_KEY", "")
    if not public or not secret or "PLACEHOLDER" in public or "PLACEHOLDER" in secret:
        raise SystemExit("Не налаштовані справжні ключі Langfuse. "
                         "Скопіюй .env.example у .env, встав API Keys із Langfuse і повтори.")
    for task in tasks:
        logger.info(f"\n=== {task['id']} | очікується: {task['expected']}")
        with propagate_attributes(trace_name=f"{opts.run}-{task['id']}", tags=[opts.run]):
            run_agent(task['question'])
    get_client().flush()
    logger.info(f"\nОброблено задач: {len(tasks)}. Прогін: {opts.run}")
    for handler in logger.handlers:
        handler.flush()
    src = HERE / "logs" / f"{config.LAB_LOGFILE_NAME}.log"
    dst = HERE / f"lab3_{opts.run}.log"
    shutil.copy2(src, dst)
    print(f"Збережено: {dst.name} (5 задач). Траси: {opts.run}-Z1...{opts.run}-P2")


if __name__ == '__main__':
    main()
