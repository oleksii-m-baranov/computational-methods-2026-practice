"""П'ять незмінних задач; --baseline вмикає старий пошук для контрольного прогону."""
import json
import sys
from langfuse import get_client, propagate_attributes
import config
import schemas
from arguments import ARGS
from agent import run_agent
from utils.lab_logger import custom_logger


def main():
    baseline = "--baseline" in sys.argv
    name = "run_lab4" if baseline else "run_rag"
    if baseline:
        config.ALLOWED[0] = "search_recipes"
        schemas.SCHEMAS[0]["function"] = {"name": "search_recipes", "description": schemas.DESCRIPTIONS["search_recipes"], "parameters": ARGS["search_recipes"].model_json_schema()}
    logger = custom_logger(name, overwrite=True)
    logger.info(f"Контрольний прогін: model={config.MODEL}, ctx={config.NUM_CTX}, baseline={baseline}")
    with open("tasks.json", encoding="utf-8") as f:
        tasks = json.load(f)
    for task in tasks:
        logger.info(f"=== {task['id']} | Очікується: {task['expected']}")
        with propagate_attributes(trace_name=f"{name}-{task['id']}", tags=[name]):
            run_agent(task["question"], logfile_name=name, task_id=task["id"], log_overwrite=False)
    get_client().flush()
    logger.info(f"Оброблено завдань: {len(tasks)}")

if __name__ == "__main__":
    main()
