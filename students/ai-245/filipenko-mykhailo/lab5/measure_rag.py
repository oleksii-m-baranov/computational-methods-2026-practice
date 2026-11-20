
"""Вимірювання RAG-агента: три описи інструмента пошуку.

Запуск:
    python measure_rag.py
    python measure_rag.py B 1
"""

import csv
import json
import os
import re
import statistics
import sys

from langfuse import get_client, propagate_attributes

import agent
import rag
import schemas
from utils.lab_logger import custom_logger


CONFIGS = ["A", "B", "C"]

names = [sys.argv[1]] if len(sys.argv) > 1 else CONFIGS
repeats = int(sys.argv[2]) if len(sys.argv) > 2 else 3

with open("rag_cases.json", encoding="utf-8") as f:
    cases = json.load(f)

UNKNOWN = (
    "не знайш",
    "не знайд",
    "немає інформац",
    "немає даних",
    "відсутн",
    "не вказан",
    "не містить",
    "не маю інформац",
    "не можу знайти",
    "нічого схожого",
    "не зазначен",
)


def norm(text):
    return re.sub(r"\s+", " ", text).strip()


def contains_value(answer, expected):
    if not answer:
        return False

    text = re.sub(r"(?<=\d)[ ](?=\d{3}\b)", "", answer)
    text = re.sub(r"(?<=\d),(?=\d)", ".", text)

    if re.fullmatch(r"\d+(\.\d+)?", expected):
        return re.search(
            rf"(?<![\d.]){re.escape(expected)}(?!\d|\.\d)",
            text
        ) is not None

    return expected.lower() in text.lower()


def admits_unknown(answer):
    return bool(answer) and any(
        word in answer.lower() for word in UNKNOWN
    )


def classify(case, searches, hit, correct):
    if case["kind"] == "none":
        return "refused" if correct else "invented"

    if correct:
        return "ok"

    if searches == 0:
        return "no_search"

    return "miss" if not hit else "ignored"


os.makedirs("results", exist_ok=True)

rows = []

for repeat in range(1, repeats + 1):
    for name in names:
        schemas.set_description(
            "search_docs",
            schemas.RAG_DESCRIPTIONS[name]
        )

        log_name = f"rag_{name}-r{repeat}"
        logger = custom_logger(log_name, overwrite=True)

        for case in cases:
            rag.TRACE.clear()

            run_id = f"{name}-r{repeat}-{case['id']}"
            logger.info(f"\n##### {run_id}")

            with propagate_attributes(
                trace_name=f"rag-{run_id}",
                tags=[f"rag-{name}"]
            ):
                answer = agent.run_agent(
                    case["question"],
                    logfile_name=log_name,
                    task_id=run_id,
                    log_overwrite=False
                )

            searches = len(rag.TRACE)

            hit = (
                case["kind"] != "none"
                and any(
                    norm(case["must_contain"]) in norm(r["text"])
                    for t in rag.TRACE
                    for r in t["results"]
                )
            )

            if case["kind"] == "none":
                correct = admits_unknown(answer)
            else:
                correct = contains_value(
                    answer,
                    case["expected"]
                )

            top_score = ""
            if searches and rag.TRACE[0]["top_score"] is not None:
                top_score = round(
                    rag.TRACE[0]["top_score"],
                    3
                )

            rows.append({
                "config": name,
                "repeat": repeat,
                "id": case["id"],
                "kind": case["kind"],
                "searches": searches,
                "hit": int(hit),
                "correct": int(correct),
                "category": classify(
                    case, searches, hit, correct
                ),
                "top_score": top_score,
                "answer": (answer or "").replace("\n", " ")[:300],
                **{
                    k: agent.LAST_RUN[k]
                    for k in (
                        "status",
                        "steps",
                        "prompt_tokens",
                        "completion_tokens",
                        "seconds"
                    )
                }
            })

get_client().flush()

path = "results/rag.csv"
old = []

if os.path.exists(path):
    with open(path, encoding="utf-8", newline="") as f:
        old = [
            r for r in csv.DictReader(f)
            if r["config"] not in names
        ]

with open(path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=list(rows[0].keys())
    )
    writer.writeheader()
    writer.writerows(old + rows)

print("\n=== Підсумок ===")

for name in names:
    part = [r for r in rows if r["config"] == name]
    answerable = [
        r for r in part if r["kind"] != "none"
    ]

    right = sum(r["correct"] for r in answerable)
    searched = sum(
        1 for r in answerable if r["searches"] > 0
    )

    median_steps = statistics.median(
        r["steps"] for r in part
    )

    print(
        f"{name}: правильно {right}/{len(answerable)} | "
        f"викликали пошук у {searched}/{len(answerable)} | "
        f"кроків (медіана) {median_steps}"
    )

print("Детальні таблиці: python rag_report.py")
