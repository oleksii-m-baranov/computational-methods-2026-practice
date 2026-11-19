"""Векторний індекс: побудова, збереження, завантаження, пошук.

faiss-cpu не має збірки для Python 3.15, тому, як дозволяє методичка (крок 4),
FAISS замінено індексом на numpy з лекції 9 (п. 9.7). Інтерфейс класу Index той самий:
повний перебір і скалярний добуток нормалізованих векторів, як у faiss.IndexFlatIP."""
import json
import os

import numpy as np

import chunking
import config
import embedder



def normalize_L2(matrix):
    """Нормалізує кожен рядок матриці до довжини 1 (на місці), як faiss.normalize_L2."""
    matrix /= np.linalg.norm(matrix, axis=1, keepdims=True)


class FlatIP:
    """Мінімальна заміна faiss.IndexFlatIP: зберігає вектори й шукає за скалярним добутком."""

    def __init__(self, d):
        self.d = d                                       # довжина вектора
        self.vectors = np.zeros((0, d), dtype="float32")

    def add(self, matrix):
        self.vectors = np.vstack([self.vectors, matrix])

    def search(self, q, k):
        """Повертає (схожості, номери) розміру 1 x k; як і FAISS, доповнює -1, якщо чанків менше за k."""
        scores = self.vectors @ q[0]
        order = np.argsort(-scores)[:k]
        top_scores = np.full((1, k), -1.0, dtype="float32")
        top_ids = np.full((1, k), -1, dtype="int64")
        top_scores[0, :len(order)] = scores[order]
        top_ids[0, :len(order)] = order
        return top_scores, top_ids


TRACE = []        # записи про виклики пошуку; їх читає measure_rag.py
_index = None     # поточний індекс, який використовує інструмент search_docs


def settings():
    """Параметри, від яких залежить індекс. Зберігаються разом з ним."""
    return {"embed_model": config.EMBED_MODEL, "method": config.CHUNK_METHOD,
            "size": config.CHUNK_SIZE, "overlap": config.CHUNK_OVERLAP,
            "with_title": config.WITH_TITLE, "dirs": config.DOC_DIRS}


class Index:
    def __init__(self, chunks, vectors, meta=None):
        self.chunks = chunks
        self.meta = meta or {}
        matrix = np.array(vectors, dtype="float32")
        normalize_L2(matrix)                            # довжина кожного вектора стає 1
        self.faiss = FlatIP(matrix.shape[1])            # IP = скалярний добуток = косинус для нормалізованих
        self.faiss.add(matrix)

    @classmethod
    def build(cls, chunks):
        vectors = embedder.embed([c["text"] for c in chunks])
        return cls(chunks, vectors, settings())

    def search(self, query, k=3):
        """Повертає до k найближчих чанків: [{"score", "source", "chunk", "text"}], від найближчого."""
        q = np.array(embedder.embed([query]), dtype="float32")
        normalize_L2(q)
        scores, ids = self.faiss.search(q, k)
        result = []
        for score, i in zip(scores[0], ids[0]):
            if i == -1:                                  # чанків менше за k: FAISS заповнює -1
                continue
            result.append({"score": float(score), **self.chunks[i]})
        return result

    def save(self, directory=None):
        directory = directory or config.INDEX_DIR
        os.makedirs(directory, exist_ok=True)
        np.save(os.path.join(directory, "docs.npy"), self.faiss.vectors)   # замість docs.faiss
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
            raise RuntimeError("Індекс збудовано з іншими параметрами, ніж у config.py. "
                               f"В індексі: {meta}. У config.py: {settings()}. Перебудуйте: python build_index.py")
        obj = cls.__new__(cls)
        vectors = np.load(os.path.join(directory, "docs.npy"))
        obj.faiss = FlatIP(vectors.shape[1])
        obj.faiss.add(vectors)
        with open(os.path.join(directory, "chunks.json"), encoding="utf-8") as f:
            obj.chunks = json.load(f)
        obj.meta = meta
        return obj


def build_from_config():
    docs = chunking.load_documents(config.DOC_DIRS)
    chunks = chunking.make_chunks(docs, config.CHUNK_METHOD, config.CHUNK_SIZE,
                                  config.CHUNK_OVERLAP, config.WITH_TITLE)
    return Index.build(chunks)


def set_index(index):
    global _index
    _index = index


def get_index():
    global _index
    if _index is None:
        _index = Index.load()
    return _index