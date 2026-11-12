"""Векторний індекс FAISS: побудова, збереження, завантаження та пошук."""

import json
import os

import faiss
import numpy as np

import chunking
import config
import embedder

TRACE = []
_index = None


def settings():
    """Параметри, від яких залежить індекс."""
    return {
        "embed_model": config.EMBED_MODEL,
        "method": config.CHUNK_METHOD,
        "size": config.CHUNK_SIZE,
        "overlap": config.CHUNK_OVERLAP,
        "with_title": config.WITH_TITLE,
        "dirs": config.DOC_DIRS,
    }


class Index:
    def __init__(self, chunks, vectors, meta=None):
        self.chunks = chunks
        self.meta = meta or {}

        matrix = np.asarray(vectors, dtype="float32")
        if matrix.ndim != 2 or len(matrix) == 0:
            raise ValueError("Індекс потребує непорожню матрицю векторів")

        matrix = np.ascontiguousarray(matrix)
        faiss.normalize_L2(matrix)

        self.faiss = faiss.IndexFlatIP(matrix.shape[1])
        self.faiss.add(matrix)

    @classmethod
    def build(cls, chunks):
        vectors = embedder.embed([c["text"] for c in chunks])
        return cls(chunks, vectors, settings())

    def search(self, query, k=3):
        """Повертає до k найближчих чанків."""
        q = np.asarray(embedder.embed([query]), dtype="float32")
        q = np.ascontiguousarray(q)

        if q.ndim != 2 or q.shape[1] != self.faiss.d:
            raise ValueError("Неправильна розмірність вектора запиту")

        faiss.normalize_L2(q)
        scores, ids = self.faiss.search(q, k)

        result = []
        for score, i in zip(scores[0], ids[0]):
            if i == -1:
                continue

            result.append({
                "score": float(score),
                **self.chunks[int(i)],
            })

        return result

    def save(self, directory=None):
        directory = directory or config.INDEX_DIR
        os.makedirs(directory, exist_ok=True)

        faiss.write_index(
            self.faiss,
            os.path.join(directory, "docs.faiss"),
        )

        with open(
            os.path.join(directory, "chunks.json"),
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(self.chunks, f, ensure_ascii=False, indent=1)

        with open(
            os.path.join(directory, "meta.json"),
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(self.meta, f, ensure_ascii=False, indent=1)

    @classmethod
    def load(cls, directory=None):
        directory = directory or config.INDEX_DIR

        with open(
            os.path.join(directory, "meta.json"),
            encoding="utf-8",
        ) as f:
            meta = json.load(f)

        if meta != settings():
            raise RuntimeError(
                "Індекс побудовано з іншими параметрами, ніж у config.py. "
                f"В індексі: {meta}. У config.py: {settings()}. "
                "Перебудуйте: python build_index.py"
            )

        obj = cls.__new__(cls)

        obj.faiss = faiss.read_index(
            os.path.join(directory, "docs.faiss")
        )

        with open(
            os.path.join(directory, "chunks.json"),
            encoding="utf-8",
        ) as f:
            obj.chunks = json.load(f)

        obj.meta = meta

        if obj.faiss.ntotal != len(obj.chunks):
            raise RuntimeError(
                "Кількість векторів FAISS не збігається з кількістю чанків"
            )

        return obj


def build_from_config():
    docs = chunking.load_documents(config.DOC_DIRS)

    chunks = chunking.make_chunks(
        docs,
        config.CHUNK_METHOD,
        config.CHUNK_SIZE,
        config.CHUNK_OVERLAP,
        config.WITH_TITLE,
    )

    return Index.build(chunks)


def set_index(index):
    global _index
    _index = index


def get_index():
    global _index

    if _index is None:
        _index = Index.load()

    return _index
