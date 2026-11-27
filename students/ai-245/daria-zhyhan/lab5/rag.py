"""Векторний індекс на NumPy: побудова, збереження, завантаження, пошук."""
import json
import os

import numpy as np

import chunking
import config
import embedder

TRACE = []     
_index = None     


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


class Index:
    def __init__(self, chunks, vectors, meta=None):
        self.chunks = chunks
        self.meta = meta or {}
        matrix = np.array(vectors, dtype="float32")
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self.matrix = matrix / norms
        self.dim = self.matrix.shape[1]

    @classmethod
    def build(cls, chunks):
        vectors = embedder.embed([c["text"] for c in chunks])
        return cls(chunks, vectors, settings())

    def search(self, query, k=3):
        """Повертає до k найближчих чанків: [{"score", "source", "chunk", "text"}], від найближчого."""
        if len(self.chunks) == 0:
            return []
        q = np.array(embedder.embed([query])[0], dtype="float32")
        norm = np.linalg.norm(q)
        if norm > 0:
            q = q / norm
        scores = self.matrix @ q
        top_k = min(k, len(self.chunks))
        ids = np.argsort(-scores)[:top_k]
        return [{"score": float(scores[i]), **self.chunks[int(i)]} for i in ids]

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
        obj.matrix = np.load(os.path.join(directory, "vectors.npy"))
        obj.dim = obj.matrix.shape[1]
        with open(os.path.join(directory, "chunks.json"), encoding="utf-8") as f:
            obj.chunks = json.load(f)
        obj.meta = meta
        return obj


def build_from_config():
    docs = chunking.load_documents(config.DOC_DIRS)
    chunks = chunking.make_chunks(
        docs, config.CHUNK_METHOD, config.CHUNK_SIZE, config.CHUNK_OVERLAP, config.WITH_TITLE
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