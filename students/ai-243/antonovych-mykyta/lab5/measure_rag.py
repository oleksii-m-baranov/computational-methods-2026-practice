"""Вимірювання RAG-агента: три описи інструмента пошуку, по кілька повторів.

Запуск:
    python measure_rag.py              усі описи (A, B, C), по 3 повтори
    python measure_rag.py B 1          один опис, один повтор
"""
import argparse
import csv
import json
import re
import statistics
from pathlib import Path

from langfuse import get_client, propagate_attributes

import agent
import config
import rag
import schemas
from utils.lab_logger import custom_logger

CONFIGS = ["A", "B", "C"]

with open("rag_cases.json", encoding="utf-8") as f:
    cases = json.load(f)

UNKNOWN = ("не знайш", "не знайд", "немає інформац", "не має інформац", "немає даних", "відсутн", "не вказан",
           "не містить", "не маю інформац", "не можу знайти", "нічого схожого", "не відомо", "немає інструмен",
           "не зазначен", "не знаю", "немає в", "не маю доступ", "не можу відповіс",
           "немає конкретного", "не вдалося знайти", "відповіді немає", "в довіднику немає продукту")


def norm(text):
    return re.sub(r"\s+", " ", text).strip()


def contains_value(answer, expected):
    """Чи є очікуване значення у відповіді як окреме число або слово. Неправильні відповіді перевіряйте вручну."""
    if not answer:
        return False
    text = re.sub(r"(?<=\d)[  ](?=\d{3}\b)", "", answer)     # "1 000" -> "1000"
    text = re.sub(r"(?<=\d),(?=\d)", ".", text)                   # "13,5" -> "13.5"
    if re.fullmatch(r"\d+(\.\d+)?", expected):
        return re.search(rf"(?<![\d.]){re.escape(expected)}(?!\d|\.\d)", text) is not None
    return expected.lower() in text.lower()


def admits_unknown(answer):
    """Чи визнає відповідь, що інформації немає. Автоматична перевірка груба: перегляньте ці відповіді вручну."""
    return bool(answer and answer.strip()) and any(word in answer.lower() for word in UNKNOWN)


def classify(case, searches, hit, correct, answer):
    if case["kind"] == "none":
        if not answer or not answer.strip():
            return "no_final"
        if correct:
            return "refused"
        return "invented" if re.search(r"[0-9]", answer) else "unsupported"
    if correct:
        return "ok"
    if searches == 0:
        return "no_search"
    return "miss" if not hit else "ignored"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("description", nargs="?", choices=["all", *CONFIGS], default="all")
    parser.add_argument("repeats", nargs="?", type=int, default=3)
    parser.add_argument("--case", choices=[case["id"] for case in cases])
    parser.add_argument("--start-repeat", type=int, default=1)
    args = parser.parse_args()
    if args.repeats < 1 or args.start_repeat < 1:
        parser.error("repeats and --start-repeat must be positive")
    names = CONFIGS if args.description == "all" else [args.description]
    selected = [case for case in cases if args.case is None or case["id"] == args.case]
    path = Path("results/rag.csv")
    path.parent.mkdir(exist_ok=True)
    rows = {}
    if path.exists():
        with path.open(encoding="utf-8", newline="") as stream:
            rows = {(row["config"], int(row["repeat"]), row["id"]): row
                    for row in csv.DictReader(stream)}

    for repeat in range(args.start_repeat, args.start_repeat + args.repeats):
        for name in names:
            schemas.set_description("search_docs", schemas.RAG_DESCRIPTIONS[name])
            log_name = f"rag_{name}-r{repeat}" + (f"-{args.case}-replay" if args.case else "")
            logger = custom_logger(log_name, overwrite=True)
            for case in selected:
                rag.TRACE.clear()
                run_id = f"{name}-r{repeat}-{case['id']}"
                logger.info(f"\n##### {run_id}")
                trace_name = f"rag-{run_id}"
                with (
                    get_client().start_as_current_observation(name=trace_name, as_type="span"),
                    propagate_attributes(trace_name=trace_name, tags=[f"rag-{name}"]),
                ):
                    answer = agent.run_agent(case["question"], logfile_name=log_name, task_id=run_id)
                searches = len(rag.TRACE)
                hit = case["kind"] != "none" and any(
                    norm(case["must_contain"]) in norm(row["text"])
                    for trace in rag.TRACE for row in trace["results"])
                correct = (admits_unknown(answer) if case["kind"] == "none"
                           else contains_value(answer, case["expected"]))
                score = rag.TRACE[0]["top_score"] if searches else None
                rows[name, repeat, case["id"]] = {
                    "config": name, "repeat": repeat, "id": case["id"], "kind": case["kind"],
                    "searches": searches, "hit": int(hit), "correct": int(correct),
                    "category": classify(case, searches, hit, correct, answer),
                    "top_score": round(score, 3) if score is not None else "",
                    "answer": (answer or "").replace("\n", " ").strip(),
                    **{field: agent.LAST_RUN[field] for field in ("status", "steps", "prompt_tokens",
                                                                "completion_tokens", "seconds")},
                }
                temporary = path.with_suffix(".tmp")
                with temporary.open("w", newline="", encoding="utf-8") as stream:
                    writer = csv.DictWriter(stream, fieldnames=list(next(iter(rows.values()))),
                                            lineterminator="\n")
                    writer.writeheader()
                    writer.writerows(rows.values())
                temporary.replace(path)

    get_client().flush()
    for name in names:
        part = [r for (mode, _, _), r in rows.items() if mode == name and r["kind"] != "none"]
        right = sum(int(r["correct"]) for r in part)
        searched = sum(int(r["searches"]) > 0 for r in part)
        print(f"{name}: правильно {right}/{len(part)} | шукали {searched}/{len(part)} | "
              f"кроків (медіана) {statistics.median(int(r['steps']) for r in part):g}" if part
              else f"{name}: немає рядків з питаннями, що мають відповідь")


if __name__ == "__main__":
    main()
