
"""Порівняння шести конфігурацій чанкінгу RAG."""

import csv
import json
from pathlib import Path

import faiss
import numpy as np

import config
from chunking import load_documents, make_chunks
from embedder import embed_texts


CONFIGURATIONS = [
    {
        "name": "fixed_400",
        "method": "fixed",
        "size": 400,
        "overlap": 0,
        "with_title": False,
    },
    {
        "name": "fixed_800",
        "method": "fixed",
        "size": 800,
        "overlap": 0,
        "with_title": False,
    },
    {
        "name": "fixed_800_overlap",
        "method": "fixed",
        "size": 800,
        "overlap": 100,
        "with_title": False,
    },
    {
        "name": "paragraphs_400",
        "method": "paragraphs",
        "size": 400,
        "overlap": 0,
        "with_title": False,
    },
    {
        "name": "paragraphs_800",
        "method": "paragraphs",
        "size": 800,
        "overlap": 0,
        "with_title": False,
    },
    {
        "name": "paragraphs_800_title",
        "method": "paragraphs",
        "size": 800,
        "overlap": 0,
        "with_title": True,
    },
]


def source_name(chunk):
    return Path(chunk["source"]).name


def evaluate_configuration(setting, documents, cases, query_vectors):
    chunks = make_chunks(
        documents,
        method=setting["method"],
        size=setting["size"],
        overlap=setting["overlap"],
        with_title=setting["with_title"],
    )

    if not chunks:
        raise RuntimeError(
            f"Немає чанків для {setting['name']}"
        )

    vectors = embed_texts(
        [chunk["text"] for chunk in chunks]
    )

    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(np.asarray(vectors, dtype=np.float32))

    scores, indices = index.search(
        np.asarray(query_vectors, dtype=np.float32),
        min(3, len(chunks)),
    )

    correct_top1 = 0
    correct_top3 = 0
    evaluated = 0
    details = []

    for position, case in enumerate(cases):
        expected_source = case.get("source")

        retrieved = [
            {
                "source": source_name(chunks[int(idx)]),
                "score": float(score),
            }
            for score, idx in zip(
                scores[position],
                indices[position],
            )
            if idx >= 0
        ]

        top1 = retrieved[0] if retrieved else None

        if expected_source is None:
            status = "MANUAL"
        else:
            evaluated += 1

            top1_match = (
                top1 is not None
                and top1["source"] == expected_source
            )

            top3_match = any(
                item["source"] == expected_source
                for item in retrieved
            )

            correct_top1 += int(top1_match)
            correct_top3 += int(top3_match)

            status = "PASS" if top1_match else "FAIL"

        details.append({
            "configuration": setting["name"],
            "case_id": case["id"],
            "type": case["type"],
            "expected_source": expected_source or "",
            "top1_source": (
                top1["source"] if top1 else ""
            ),
            "top1_score": (
                round(top1["score"], 4)
                if top1 else 0
            ),
            "top3_sources": "; ".join(
                item["source"] for item in retrieved
            ),
            "status": status,
        })

    summary = {
        "configuration": setting["name"],
        "method": setting["method"],
        "chunk_size": setting["size"],
        "overlap": setting["overlap"],
        "with_title": setting["with_title"],
        "chunks": len(chunks),
        "evaluated": evaluated,
        "top1_correct": correct_top1,
        "top1_accuracy": round(
            correct_top1 / evaluated, 4
        ) if evaluated else 0,
        "top3_correct": correct_top3,
        "top3_accuracy": round(
            correct_top3 / evaluated, 4
        ) if evaluated else 0,
    }

    return summary, details


def save_csv(path, rows):
    if not rows:
        return

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


def main():
    with open(
        "rag_cases.json",
        "r",
        encoding="utf-8",
    ) as file:
        cases = json.load(file)

    documents = load_documents(config.DOC_DIRS)

    print(f"Документів: {len(documents)}")
    print(f"Тестових запитань: {len(cases)}")
    print("Обчислюємо ембединги запитань...")

    query_vectors = embed_texts(
        [case["question"] for case in cases]
    )

    summaries = []
    all_details = []

    for setting in CONFIGURATIONS:
        print()
        print("=" * 55)
        print("Конфігурація:", setting["name"])

        summary, details = evaluate_configuration(
            setting,
            documents,
            cases,
            query_vectors,
        )

        summaries.append(summary)
        all_details.extend(details)

        print("Кількість чанків:", summary["chunks"])
        print(
            "TOP-1:",
            f"{summary['top1_correct']}/"
            f"{summary['evaluated']}",
        )
        print(
            "TOP-3:",
            f"{summary['top3_correct']}/"
            f"{summary['evaluated']}",
        )

    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)

    save_csv(
        output_dir / "rag_chunking_summary.csv",
        summaries,
    )

    save_csv(
        output_dir / "rag_chunking_details.csv",
        all_details,
    )

    print()
    print("=" * 55)
    print("ЕКСПЕРИМЕНТ ЗАВЕРШЕНО")
    print("Збережено:")
    print("results/rag_chunking_summary.csv")
    print("results/rag_chunking_details.csv")
    print()
    print(
        "Основний FAISS-індекс не змінювався."
    )


if __name__ == "__main__":
    main()
