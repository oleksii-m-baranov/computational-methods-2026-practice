
"""Автоматична перевірка RAG-пошуку для лабораторної №5."""

import csv
import json
import os

from rag import search_docs


def main():
    with open("rag_cases.json", "r", encoding="utf-8") as file:
        cases = json.load(file)

    os.makedirs("results", exist_ok=True)

    rows = []
    correct = 0

    for case in cases:
        question = case["question"]
        expected_source = case.get("source")
        expected_answer = case.get("expected")

        results = search_docs(question)

        top_source = (
            os.path.basename(results[0]["source"])
            if results
            else ""
        )

        top_score = (
            round(results[0]["score"], 3)
            if results
            else 0
        )

        if expected_source is None:
            # Без еталонного джерела не можна автоматично
            # визначити, чи агент правильно відмовиться.
            status = "MANUAL"
        elif top_source == expected_source:
            status = "PASS"
            correct += 1
        else:
            status = "FAIL"

        rows.append({
            "id": case["id"],
            "type": case["type"],
            "question": question,
            "expected": expected_answer or "",
            "expected_source": expected_source or "",
            "top_source": top_source,
            "top_score": top_score,
            "status": status,
        })

        print(
            f"{case['id']}: {status} | "
            f"джерело={top_source} | "
            f"score={top_score}"
        )

    path = "results/rag_retrieval_cases.csv"

    with open(
        path,
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(rows[0].keys()),
        )
        writer.writeheader()
        writer.writerows(rows)

    answerable = sum(
        case.get("source") is not None
        for case in cases
    )

    print()
    print(f"Правильне джерело TOP-1: {correct}/{answerable}")
    print("Запитання без відповіді: потребують окремої перевірки")
    print(f"Результати збережено: {path}")


if __name__ == "__main__":
    main()
