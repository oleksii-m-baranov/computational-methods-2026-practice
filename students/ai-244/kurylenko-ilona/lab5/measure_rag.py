"""Вимірювання RAG-агента: три описи інструмента пошуку, по кілька повторів.

Запуск:
    python measure_rag.py              усі описи (A, B, C), по 3 повтори
    python measure_rag.py B 1          один опис, один повтор
"""
import csv
import json
import os
import re
import statistics
import sys

from langfuse import get_client, propagate_attributes

import agent
import config
import rag
import schemas
from utils.lab_logger import custom_logger

CONFIGS = ["A", "B", "C"]                      # ключі зі schemas.RAG_DESCRIPTIONS
names = [sys.argv[1]] if len(sys.argv) > 1 else CONFIGS
repeats = int(sys.argv[2]) if len(sys.argv) > 2 else 3

with open("rag_cases.json", encoding="utf-8") as f:
    cases = json.load(f)

UNKNOWN = ("не знайш", "не знайд", "немає інформац", "не має інформац", "немає даних", "відсутн", "не вказан",
           "не містить", "не маю інформац", "не можу знайти", "нічого схожого", "не відомо", "немає інструмен",
           "не зазначен")


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
    return bool(answer) and any(word in answer.lower() for word in UNKNOWN)


def classify(case, searches, hit, correct):
    if case["kind"] == "none":
        return "refused" if correct else "invented"
    if correct:
        return "ok"
    if searches == 0:
        return "no_search"
    return "miss" if not hit else "ignored"


os.makedirs("results", exist_ok=True)               # папку logs/ створює custom_logger
rows = []

for repeat in range(1, repeats + 1):               # повтори - зовнішній цикл: описи чергуються
    for name in names:
        schemas.set_description("search_docs", schemas.RAG_DESCRIPTIONS[name])
        # окремий лог на кожну пару опис+повтор: logs/rag_<опис>-r<повтор>.log
        log_name = f"rag_{name}-r{repeat}"
        logger = custom_logger(log_name, overwrite=True)     # очищаємо файл один раз на початку серії

        for case in cases:
            rag.TRACE.clear()
            run_id = f"{name}-r{repeat}-{case['id']}"
            logger.info(f"\n##### {run_id}")
            with propagate_attributes(trace_name=f"rag-{run_id}", tags=[f"rag-{name}"]):
                # log_overwrite=False: агент дописує в той самий файл, а не стирає попередні питання
                answer = agent.run_agent(case["question"], logfile_name=log_name,
                                         task_id=run_id, log_overwrite=False)
            searches = len(rag.TRACE)
            hit = case["kind"] != "none" and any(norm(case["must_contain"]) in norm(r["text"])
                                                  for t in rag.TRACE for r in t["results"])
            if case["kind"] == "none":
                correct = admits_unknown(answer)
            else:
                correct = contains_value(answer, case["expected"])
            rows.append({"config": name, "repeat": repeat, "id": case["id"], "kind": case["kind"],
                         "searches": searches, "hit": int(hit), "correct": int(correct),
                         "category": classify(case, searches, hit, correct),
                         "top_score": round(rag.TRACE[0]["top_score"], 3) if searches else "",
                         "answer": (answer or "").replace("\n", " ")[:300],
                         **{k: agent.LAST_RUN[k] for k in ("status", "steps", "prompt_tokens",
                                                            "completion_tokens", "seconds")}})

            # Зберігаємо прогрес у файл
            path = "results/rag.csv"
            old = []
            if os.path.exists(path):
                with open(path, encoding="utf-8", newline="") as f:
                    old = [r for r in csv.DictReader(f) if not (r["config"] == name and int(r["repeat"]) == repeat and r["id"] == case["id"])]
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=list(rows[-1].keys()))
                writer.writeheader()
                writer.writerows(old + [rows[-1]])

            print(f"[{run_id}] correct={correct}, searches={searches}, cat={rows[-1]['category']}", flush=True)

get_client().flush()

# файл результатів: рядки з поточного запуску замінюються новими за складеним ключем
path = "results/rag.csv"
old = []
new_keys = {(r["config"], str(r["repeat"]), r["id"]) for r in rows}
if os.path.exists(path):
    with open(path, encoding="utf-8", newline="") as f:
        old = [r for r in csv.DictReader(f) if (r["config"], str(r["repeat"]), r["id"]) not in new_keys]
with open(path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(old + rows)

print("\n=== Підсумок ===")
for name in names:
    part = [r for r in rows if r["config"] == name]
    answerable = [r for r in part if r["kind"] != "none"]
    print(f"{name}: правильно {sum(r['correct'] for r in answerable)}/{len(answerable)} | "
          f"викликали пошук у {sum(1 for r in answerable if r['searches'] > 0)}/{len(answerable)} | "
          f"кроків (медіана) {statistics.median(r['steps'] for r in part)}")
print("Детальні таблиці: python rag_report.py")
