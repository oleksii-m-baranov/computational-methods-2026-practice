
"""Порівняння описів RAG-інструмента A, B і C."""

import argparse
import csv
import json
import time
from pathlib import Path

import agent
import config
import schemas


OUTPUT = Path("results/description_comparison.csv")

FIELDS = [
    "variant",
    "repeat",
    "case_id",
    "case_type",
    "question",
    "answer",
    "success",
    "steps",
    "search_docs_calls",
    "tool_calls",
    "prompt_tokens",
    "completion_tokens",
    "total_tokens",
    "duration_seconds",
]


def set_description(variant):
    """Встановлює опис search_docs для поточного тесту."""

    config.DOCS_DESCRIPTION = variant

    for tool_schema in schemas.SCHEMAS:
        if tool_schema["function"]["name"] == "search_docs":
            tool_schema["function"]["description"] = (
                schemas.RAG_DESCRIPTIONS[variant]
            )
            return

    raise RuntimeError(
        "Інструмент search_docs не знайдено у SCHEMAS"
    )


def load_completed():
    """Зчитує вже виконані тести з CSV."""

    completed = set()

    if not OUTPUT.exists():
        return completed

    with OUTPUT.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            key = (
                row["variant"],
                int(row["repeat"]),
                row["case_id"],
            )
            completed.add(key)

    return completed


def save_result(row):
    """Одразу записує результат одного тесту."""

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_exists = (
        OUTPUT.exists()
        and OUTPUT.stat().st_size > 0
    )

    with OUTPUT.open(
        "a",
        encoding="utf-8-sig" if not file_exists else "utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=FIELDS,
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow(row)


def main():
    parser = argparse.ArgumentParser(
        description="Експеримент A/B/C для RAG-агента"
    )

    parser.add_argument(
        "--repeats",
        type=int,
        default=3,
        help="Кількість повторень кожного тесту",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Кількість запитань",
    )

    parser.add_argument(
        "--variants",
        nargs="+",
        choices=["A", "B", "C"],
        default=["A", "B", "C"],
        help="Варіанти описів інструмента",
    )

    args = parser.parse_args()

    if args.repeats < 1:
        parser.error("--repeats має бути >= 1")

    if args.limit < 1:
        parser.error("--limit має бути >= 1")

    with open(
        "rag_cases.json",
        "r",
        encoding="utf-8",
    ) as file:
        cases = json.load(file)

    cases = cases[:args.limit]

    completed = load_completed()

    total = (
        len(args.variants)
        * args.repeats
        * len(cases)
    )

    current = 0
    skipped = 0
    executed = 0

    print("=" * 60)
    print("ЕКСПЕРИМЕНТ A/B/C")
    print("Усього заплановано:", total)
    print("Уже є записів у CSV:", len(completed))
    print("=" * 60)

    for variant in args.variants:
        set_description(variant)

        for repeat in range(1, args.repeats + 1):
            for case in cases:
                current += 1

                key = (
                    variant,
                    repeat,
                    case["id"],
                )

                if key in completed:
                    skipped += 1

                    print(
                        f"Пропущено виконаний тест: "
                        f"{variant}, повтор {repeat}, "
                        f"{case['id']}",
                        flush=True,
                    )
                    continue

                print()
                print("=" * 60)
                print(
                    f"Тест {current}/{total}: "
                    f"{variant}, повтор {repeat}, "
                    f"{case['id']}",
                    flush=True,
                )

                start = time.perf_counter()

                try:
                    answer = agent.run_agent(
                        case["question"]
                    )

                    stats = dict(agent.LAST_RUN)
                    error = ""

                except Exception as exc:
                    answer = None
                    stats = {}
                    error = str(exc)

                    print(
                        "Помилка:",
                        error,
                        flush=True,
                    )

                duration = (
                    time.perf_counter() - start
                )

                row = {
                    "variant": variant,
                    "repeat": repeat,
                    "case_id": case["id"],
                    "case_type": case["type"],
                    "question": case["question"],
                    "answer": (
                        str(answer)
                        if answer is not None
                        else error
                    ),
                    "success": stats.get(
                        "success",
                        False,
                    ),
                    "steps": stats.get(
                        "steps",
                        0,
                    ),
                    "search_docs_calls": stats.get(
                        "search_docs_calls",
                        0,
                    ),
                    "tool_calls": json.dumps(
                        stats.get("tool_calls", []),
                        ensure_ascii=False,
                    ),
                    "prompt_tokens": stats.get(
                        "prompt_tokens",
                        0,
                    ),
                    "completion_tokens": stats.get(
                        "completion_tokens",
                        0,
                    ),
                    "total_tokens": stats.get(
                        "total_tokens",
                        0,
                    ),
                    "duration_seconds": round(
                        duration,
                        2,
                    ),
                }

                save_result(row)

                completed.add(key)
                executed += 1

                print(
                    f"Збережено: {variant} | "
                    f"{case['id']} | "
                    f"RAG={row['search_docs_calls']} | "
                    f"час={row['duration_seconds']} с",
                    flush=True,
                )

    print()
    print("=" * 60)
    print("ЕКСПЕРИМЕНТ ЗАВЕРШЕНО")
    print("Нових тестів:", executed)
    print("Пропущено виконаних:", skipped)
    print("Файл результатів:", OUTPUT)
    print("=" * 60)


if __name__ == "__main__":
    main()
