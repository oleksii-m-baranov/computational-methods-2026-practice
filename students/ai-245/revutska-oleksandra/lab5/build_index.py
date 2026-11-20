
"""Побудова FAISS-індексу для RAG."""

import json
from pathlib import Path

import faiss
import config

from chunking import load_documents, make_chunks
from embedder import embed_texts


def main():
    documents = load_documents(config.DOC_DIRS)

    chunks = make_chunks(
        documents,
        method=config.CHUNK_METHOD,
        size=config.CHUNK_SIZE,
        overlap=config.CHUNK_OVERLAP,
        with_title=config.WITH_TITLE,
    )

    if not chunks:
        raise RuntimeError("Не знайдено чанків для індексації")

    print(f"Документів: {len(documents)}")
    print(f"Чанків: {len(chunks)}")
    print("Створюємо ембединги...")

    vectors = embed_texts([chunk["text"] for chunk in chunks])

    # Вектори вже нормалізовані, тому
    # скалярний добуток відповідає косинусній схожості.
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)

    output_dir = Path(config.INDEX_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    faiss.write_index(
        index,
        str(output_dir / "docs.faiss"),
    )

    with (output_dir / "chunks.json").open(
        "w", encoding="utf-8"
    ) as file:
        json.dump(chunks, file, ensure_ascii=False, indent=2)

    print(f"Розмір вектора: {vectors.shape[1]}")
    print(f"Записів в індексі: {index.ntotal}")
    print(f"Індекс збережено в: {output_dir}")


if __name__ == "__main__":
    main()
