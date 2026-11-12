"""Контрольні запитання з лабораторної №3 на новій моделі."""
import json
from pathlib import Path
from langfuse import get_client, propagate_attributes
import config
from agent import run_agent

ROOT = Path(__file__).resolve().parent


def main():
    tasks = json.loads((ROOT / "tasks.json").read_text(encoding="utf-8"))
    for item in tasks:
        with propagate_attributes(trace_name=f"{config.RUN_TAG}-{item['id']}", tags=[config.RUN_TAG]):
            run_agent(item["question"], logfile_name="run_lab3")
    get_client().flush()
    print(f"Контрольних запитань: {len(tasks)}; лог: logs/run_lab3.log")


if __name__ == "__main__":
    main()
