"""Запуск довгої задачі в конфігураціях none, trim, trim+state, summary."""
import argparse
import json
import time
from pathlib import Path
from langfuse import get_client, propagate_attributes
import agent
import config
from table import make_row, print_table

ROOT = Path(__file__).resolve().parent
CONFIGS = {
    "none": {"COMPRESS": "none", "USE_STATE": False},
    "trim": {"COMPRESS": "trim", "USE_STATE": False},
    "trim+state": {"COMPRESS": "trim", "USE_STATE": True},
    "summary": {"COMPRESS": "summary", "USE_STATE": False},
}


def is_correct(answer, expected):
    import re
    if not answer:
        return False
    digits = str(int(expected))
    groups = []
    while digits:
        groups.insert(0, digits[-3:])
        digits = digits[:-3]
    pattern = r"[\s,._]?".join(map(re.escape, groups))
    return bool(re.search(rf"(?<!\d){pattern}(?!\d)", answer))


def run_once(name, repeat, series, task):
    for key, value in CONFIGS[name].items():
        setattr(config, key, value)
    run_id = f"{series}_{name}_r{repeat}"
    started = time.perf_counter()
    with propagate_attributes(trace_name=f"long-{run_id}", tags=[series, name]):
        answer = agent.run_agent(task["question"], max_steps=config.MAX_STEPS_LONG,
                                 logfile_name=run_id, task_id=run_id, log_overwrite=True)
    return run_id, answer, round(time.perf_counter() - started, 2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config", nargs="?", choices=["none", "trim", "trim+state", "summary", "all"], default="all")
    parser.add_argument("repeats", nargs="?", type=int, default=3)
    parser.add_argument("series", nargs="?", default="main")
    args = parser.parse_args()
    if args.repeats < 1 or not args.series.isidentifier():
        parser.error("Неправильна кількість повторів або назва серії")
    config.USE_CACHE = args.series.startswith("cache")
    task = json.loads((ROOT / "long_task.json").read_text(encoding="utf-8"))
    names = ["none", "trim", "trim+state"] if args.config == "all" else [args.config]
    rows = []
    details = []
    for repeat in range(1, args.repeats + 1):
        for name in names:
            run_id, answer, seconds = run_once(name, repeat, args.series, task)
            correct = is_correct(answer, task["expected"])
            row = make_row(run_id, name, correct, seconds)
            rows.append(row)
            details.append({"run": run_id, "answer": answer, "seconds": seconds,
                            "correct_numeric": correct, **row})
            print(f"[{run_id}] {seconds} с | збіг числа: {'так' if correct else 'ні'}")
    (ROOT / "logs").mkdir(exist_ok=True)
    (ROOT / "logs" / f"{args.series}_results.json").write_text(
        json.dumps(details, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    get_client().flush()
    print_table(rows)


if __name__ == "__main__":
    main()
