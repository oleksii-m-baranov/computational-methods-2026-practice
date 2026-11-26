"""Контроль п’яти задач після заміни пошуку."""
import json
from pathlib import Path
from langfuse import get_client, propagate_attributes
from agent import run_agent

ROOT = Path(__file__).resolve().parent

def main():
    tasks = json.loads((ROOT / "tasks.json").read_text(encoding="utf-8"))
    for item in tasks:
        with propagate_attributes(trace_name=f"rag-control-{item['id']}", tags=["rag-control"]):
            run_agent(item["question"], logfile_name="run_rag")
    get_client().flush()
    print(f"Контрольних питань: {len(tasks)}; лог: logs/run_rag.log")

if __name__ == "__main__":
    main()
