"""Векторний індекс на numpy: побудова, збереження, завантаження, пошук."""
import json
import os

import numpy as np

import chunking
import config
import embedder

TRACE = []        # записи про виклики пошуку; їх читає measure_rag.py
_index = None     # поточний індекс, який використовує інструмент search_docs


def settings():
    """Параметри, від яких залежить індекс. Зберігаються разом з ним."""
    return {
        "embed_model": config.EMBED_MODEL,
        "method": config.CHUNK_METHOD,
        "size": config.CHUNK_SIZE,
        "overlap": config.CHUNK_OVERLAP,
        "with_title": config.WITH_TITLE,
        "dirs": config.DOC_DIRS,
    }


def _normalize_rows(matrix: np.ndarray) -> np.ndarray:
    """Нормалізує кожен рядок матриці до одиничної довжини."""
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1.0, norms)
    return matrix / norms


class Index:
    def __init__(self, chunks, vectors, meta=None):
        self.chunks = chunks
        self.meta = meta or {}
        if len(chunks) == 0:
            self.matrix = np.empty((0, 0), dtype="float32")
            self.dim = 0
        else:
            raw = np.array(vectors, dtype="float32")
            self.matrix = _normalize_rows(raw)
            self.dim = int(self.matrix.shape[1])

    @classmethod
    def build(cls, chunks):
        vectors = embedder.embed([c["text"] for c in chunks])
        return cls(chunks, vectors, settings())

    def search(self, query, k=3):
        """Повертає до k найближчих чанків: [{"score", "source", "chunk", "text"}], від найближчого."""
        if not self.chunks or k <= 0:
            return []
        q = np.array(embedder.embed([query]), dtype="float32")
        q = _normalize_rows(q)
        scores = (self.matrix @ q[0])
        top_k = min(k, len(self.chunks))
        top_idx = np.argsort(-scores)[:top_k]
        result = []
        for i in top_idx:
            idx = int(i)
            result.append({"score": float(scores[idx]), **self.chunks[idx]})
        return result

    def save(self, directory=None):
        directory = directory or config.INDEX_DIR
        os.makedirs(directory, exist_ok=True)
        np.save(os.path.join(directory, "vectors.npy"), self.matrix)
        with open(os.path.join(directory, "chunks.json"), "w", encoding="utf-8") as f:
            json.dump(self.chunks, f, ensure_ascii=False, indent=1)
        with open(os.path.join(directory, "meta.json"), "w", encoding="utf-8") as f:
            json.dump(self.meta, f, ensure_ascii=False, indent=1)

    @classmethod
    def load(cls, directory=None):
        directory = directory or config.INDEX_DIR
        with open(os.path.join(directory, "meta.json"), encoding="utf-8") as f:
            meta = json.load(f)
        if meta != settings():
            raise RuntimeError(
                "Індекс збудовано з іншими параметрами, ніж у config.py. "
                f"В індексі: {meta}. У config.py: {settings()}. Перебудуйте: python build_index.py"
            )
        obj = cls.__new__(cls)
        vec_path = os.path.join(directory, "vectors.npy")
        if os.path.exists(vec_path):
            obj.matrix = np.load(vec_path).astype("float32")
            obj.dim = int(obj.matrix.shape[1]) if obj.matrix.ndim == 2 and obj.matrix.shape[0] > 0 else 0
        else:
            with open(os.path.join(directory, "chunks.json"), encoding="utf-8") as f:
                chunks = json.load(f)
            vectors = embedder.embed([c["text"] for c in chunks])
            raw = np.array(vectors, dtype="float32")
            obj.matrix = _normalize_rows(raw) if len(chunks) > 0 else np.empty((0, 0), dtype="float32")
            obj.dim = int(obj.matrix.shape[1]) if len(chunks) > 0 else 0
        with open(os.path.join(directory, "chunks.json"), encoding="utf-8") as f:
            obj.chunks = json.load(f)
        obj.meta = meta
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