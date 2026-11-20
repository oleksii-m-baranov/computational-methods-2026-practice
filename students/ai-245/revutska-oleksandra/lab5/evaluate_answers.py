
"""Оцінювання фактичної правильності відповідей A/B/C."""

import csv
import re
from collections import defaultdict
from pathlib import Path

INPUT = Path("results/description_comparison.csv")
OUTPUT = Path("results/answer_accuracy.csv")

EXPECTED = {
    "direct_01": r"\b6\b|шість",
    "direct_02": r"10[:.]00|десят",
    "direct_03": r"\b46\b",
    "direct_04": r"480\s*000|480000",
    "paraphrase_01": r"\b4\b|чотир",
    "paraphrase_02": r"\b21\b|двадцят[ьи]\s+од",
    "paraphrase_03": r"\b72\b|сімдесят\s+дв",
}

def normalize(text):
    return text.lower().replace("\u00a0", " ")

def evaluate(case_id, answer):
    text = normalize(answer)

    if not text.strip():
        return "incorrect"

    if case_id in EXPECTED:
        return (
            "correct"
            if re.search(EXPECTED[case_id], text)
            else "incorrect"
        )

    if case_id == "paraphrase_04":
        second = bool(
            re.search(r"\b2\b|друг", text)
        )
        fourth = bool(
            re.search(r"\b4\b|четверт", text)
        )
        return (
            "correct"
            if second and fourth
            else "incorrect"
        )

    if case_id.startswith("no_answer"):
        return "manual_review"

    return "manual_review"


def main():
    with INPUT.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        rows = list(csv.DictReader(file))

    results = []
    groups = defaultdict(list)

    for row in rows:
        verdict = evaluate(
            row["case_id"],
            row["answer"],
        )

        result = {
            "variant": row["variant"],
            "repeat": row["repeat"],
            "case_id": row["case_id"],
            "answer": row["answer"],
            "verdict": verdict,
        }

        results.append(result)
        groups[row["variant"]].append(verdict)

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
            fieldnames=[
                "variant",
                "repeat",
                "case_id",
                "answer",
                "verdict",
            ],
        )
        writer.writeheader()
        writer.writerows(results)

    print("\nПРАВИЛЬНІСТЬ ВІДПОВІДЕЙ")
    print("-" * 50)

    for variant in ["A", "B", "C"]:
        verdicts = groups[variant]

        correct = verdicts.count("correct")
        incorrect = verdicts.count("incorrect")
        manual = verdicts.count("manual_review")

        evaluated = correct + incorrect

        accuracy = (
            100 * correct / evaluated
            if evaluated
            else 0
        )

        print(f"\nВаріант {variant}")
        print(f"  Правильних: {correct}")
        print(f"  Неправильних: {incorrect}")
        print(f"  Потребують ручної перевірки: {manual}")
        print(f"  Попередня точність: {accuracy:.1f}%")

    print("\nРезультати:", OUTPUT)
    print(
        "Увага: це автоматична перевірка за ключовими "
        "фактами, а не повна семантична оцінка."
    )


if __name__ == "__main__":
    main()
