
"""Аналіз результатів експерименту A/B/C."""

import csv
from collections import defaultdict
from pathlib import Path
from statistics import mean

INPUT = Path("results/description_comparison.csv")
OUTPUT = Path("results/description_summary.csv")


def number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def main():
    with INPUT.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        rows = list(csv.DictReader(file))

    groups = defaultdict(list)

    for row in rows:
        groups[row["variant"]].append(row)

    summary = []

    for variant in ["A", "B", "C"]:
        items = groups[variant]

        if not items:
            continue

        total = len(items)

        rag_used = sum(
            number(row["search_docs_calls"]) > 0
            for row in items
        )

        empty_answers = sum(
            not row["answer"].strip()
            for row in items
        )

        successful = sum(
            row["success"].strip().lower() == "true"
            for row in items
        )

        avg_tokens = mean(
            number(row["total_tokens"])
            for row in items
        )

        avg_time = mean(
            number(row["duration_seconds"])
            for row in items
        )

        result = {
            "variant": variant,
            "tests": total,
            "rag_used": rag_used,
            "rag_rate_percent": round(
                100 * rag_used / total, 1
            ),
            "empty_answers": empty_answers,
            "technical_success": successful,
            "avg_tokens": round(avg_tokens, 1),
            "avg_seconds": round(avg_time, 1),
        }

        summary.append(result)

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(summary[0].keys()),
        )
        writer.writeheader()
        writer.writerows(summary)

    print("\nПОРІВНЯННЯ ОПИСІВ RAG")
    print("-" * 70)

    for row in summary:
        print(f"\nВаріант {row['variant']}")
        print(f"  Тестів: {row['tests']}")
        print(
            f"  Використано RAG: "
            f"{row['rag_used']} "
            f"({row['rag_rate_percent']}%)"
        )
        print(
            f"  Порожніх відповідей: "
            f"{row['empty_answers']}"
        )
        print(
            f"  Технічно успішних: "
            f"{row['technical_success']}"
        )
        print(
            f"  Середня кількість токенів: "
            f"{row['avg_tokens']}"
        )
        print(
            f"  Середній час: "
            f"{row['avg_seconds']} с"
        )

    print("\nРезультати збережено:", OUTPUT)
    print(
        "\nУвага: технічний успіх не означає "
        "фактичну правильність відповіді."
    )


if __name__ == "__main__":
    main()
