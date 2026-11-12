
"""Пошук релевантних документів за допомогою FAISS."""

import json
from pathlib import Path

import faiss

import config
from embedder import embed_query


def search_docs(query, top_k=None, min_score=None):
    """Повертає найбільш релевантні чанки для запиту."""
    top_k = config.TOP_K if top_k is None else top_k
    min_score = config.MIN_SCORE if min_score is None else min_score

    index_dir = Path(config.INDEX_DIR)
    index_path = index_dir / "docs.faiss"
    chunks_path = index_dir / "chunks.json"

    if not index_path.exists() or not chunks_path.exists():
        raise FileNotFoundError(
            "FAISS-індекс не знайдено. Запусти python build_index.py"
        )

    index = faiss.read_index(str(index_path))

    with chunks_path.open("r", encoding="utf-8") as file:
        chunks = json.load(file)

    if index.ntotal != len(chunks):
        raise ValueError("Кількість векторів і чанків не збігається")

    if top_k <= 0:
        return []

    vector = embed_query(query).reshape(1, -1)

    scores, indices = index.search(
        vector,
        min(top_k, index.ntotal),
    )

    results = []

    for score, idx in zip(scores[0], indices[0]):
        if idx < 0 or float(score) < min_score:
            continue

        chunk = chunks[int(idx)]

        results.append({
            "id": chunk["id"],
            "source": chunk["source"],
            "title": chunk["title"],
            "text": chunk["text"],
            "score": float(score),
        })

    return results
