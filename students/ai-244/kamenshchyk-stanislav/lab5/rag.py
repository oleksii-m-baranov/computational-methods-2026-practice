"""Векторний індекс на FAISS (або на numpy, якщо faiss-cpu не встановлено): побудова, збереження, завантаження, пошук."""
import json
import os

import numpy as np

try:
    import faiss                  # якщо faiss-cpu встановлено, індекс будує FAISS
except ImportError:               # faiss-cpu не встановлюється на Python 3.15: індекс на numpy (лекція 9, п. 9.7)
    faiss = None

import chunking
import config
import embedder

class NumpyIndexIP:
    """Заміна faiss.IndexFlatIP на numpy з тим самим інтерфейсом: d, add, search.
    Пошук - повний перебір: скалярний добуток запиту з кожним вектором (для нормалізованих = косинус)."""

    def __init__(self, d):
        self.d = d
        self.matrix = np.zeros((0, d), dtype="float32")

    def add(self, matrix):
        self.matrix = np.vstack([self.matrix, matrix.astype("float32")])

    def search(self, queries, k):
        scores = queries @ self.matrix.T                       # схожість з кожним чанком
        k_real = min(k, self.matrix.shape[0])
        order = np.argsort(-scores, axis=1)[:, :k_real]        # номери найближчих, від найближчого
        top = np.take_along_axis(scores, order, axis=1)
        if k_real < k:                                         # як FAISS: бракує чанків - заповнюємо -1
            pad = k - k_real
            order = np.hstack([order, -np.ones((len(queries), pad), dtype=int)])
            top = np.hstack([top, np.full((len(queries), pad), -1.0, dtype="float32")])
        return top, order


def normalize(matrix):
    """Ділить кожен рядок на його довжину, на місці (як normalize_L2 у FAISS)."""
    matrix /= np.linalg.norm(matrix, axis=1, keepdims=True)


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
        normalize(matrix)                                # довжина кожного вектора стає 1
        # IP = скалярний добуток = косинус для нормалізованих
        self.faiss = faiss.IndexFlatIP(matrix.shape[1]) if faiss else NumpyIndexIP(matrix.shape[1])
        self.faiss.add(matrix)

    @classmethod
    def build(cls, chunks):
        vectors = embedder.embed([c["text"] for c in chunks])
        return cls(chunks, vectors, settings())

    def search(self, query, k=3):
        """Повертає до k найближчих чанків: [{"score", "source", "chunk", "text"}], від найближчого."""
        q = np.array(embedder.embed([query]), dtype="float32")
        normalize(q)
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
        if faiss:
            faiss.write_index(self.faiss, os.path.join(directory, "docs.faiss"))
        else:
            np.save(os.path.join(directory, "docs.npy"), self.faiss.matrix)   # вектори чанків
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
        if faiss:
            obj.faiss = faiss.read_index(os.path.join(directory, "docs.faiss"))
        else:
            matrix = np.load(os.path.join(directory, "docs.npy"))
            obj.faiss = NumpyIndexIP(matrix.shape[1])
            obj.faiss.add(matrix)
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