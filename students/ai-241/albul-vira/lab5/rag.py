"""Векторний індекс на ChromaDB: побудова, збереження, завантаження, пошук."""
import json
import os

os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")

import chromadb

import chunking
import config
import embedder

TRACE = []        # записи про виклики пошуку; їх читає measure_rag.py
_index = None     # поточний індекс, який використовує інструмент search_docs


def settings():
    """Параметри, від яких залежить індекс. Зберігаються разом з ним."""
    return {"backend": "chroma", "embed_model": config.EMBED_MODEL, "method": config.CHUNK_METHOD,
            "size": config.CHUNK_SIZE, "overlap": config.CHUNK_OVERLAP,
            "with_title": config.WITH_TITLE, "dirs": config.DOC_DIRS}


def _populate_collection(client, chunks, vectors):
    try:
        client.delete_collection("docs")
    except Exception:
        pass
    collection = client.create_collection(name="docs", metadata={"hnsw:space": "cosine"})
    if chunks:
        collection.add(
            ids=[f"c{i}" for i in range(len(chunks))],
            embeddings=vectors,
            documents=[c["text"] for c in chunks],
            metadatas=[{"idx": i, "source": c["source"], "chunk": c["chunk"]} for i, c in enumerate(chunks)],
        )
    return collection


class Index:
    def __init__(self, chunks, vectors, meta=None):
        self.chunks = chunks
        self.vectors = vectors
        self.meta = meta or {}
        self.dim = len(vectors[0]) if vectors else 0
        self.client = chromadb.EphemeralClient()
        self.collection = _populate_collection(self.client, chunks, vectors)

    @classmethod
    def build(cls, chunks):
        vectors = embedder.embed([c["text"] for c in chunks])
        return cls(chunks, vectors, settings())

    def search(self, query, k=3):
        """Повертає до k найближчих чанків: [{"score", "source", "chunk", "text"}], від найближчого."""
        if not self.chunks:
            return []
        q = embedder.embed([query])
        res = self.collection.query(
            query_embeddings=q,
            n_results=min(k, len(self.chunks)),
            include=["distances", "metadatas"],
        )
        result = []
        for dist, meta in zip(res["distances"][0], res["metadatas"][0]):
            score = 1.0 - float(dist)          # косинусна відстань -> косинусна схожість
            result.append({"score": score, **self.chunks[meta["idx"]]})
        result.sort(key=lambda item: item["score"], reverse=True)
        return result

    def save(self, directory=None):
        directory = directory or config.INDEX_DIR
        os.makedirs(directory, exist_ok=True)
        chroma_dir = os.path.join(directory, "chroma")
        self.client = chromadb.PersistentClient(path=chroma_dir)
        self.collection = _populate_collection(self.client, self.chunks, self.vectors)
        with open(os.path.join(directory, "chunks.json"), "w", encoding="utf-8") as f:
            json.dump(self.chunks, f, ensure_ascii=False, indent=1)
        with open(os.path.join(directory, "meta.json"), "w", encoding="utf-8") as f:
            json.dump(self.meta, f, ensure_ascii=False, indent=1)

    @classmethod
    def load(cls, directory=None):
        directory = directory or config.INDEX_DIR
        meta_path = os.path.join(directory, "meta.json")
        if not os.path.exists(meta_path):
            raise RuntimeError("Індекс ChromaDB не знайдено. Перебудуйте: python build_index.py")
        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)
        if meta != settings():
            raise RuntimeError("Індекс збудовано з іншими параметрами, ніж у config.py. "
                               f"В індексі: {meta}. У config.py: {settings()}. Перебудуйте: python build_index.py")
        obj = cls.__new__(cls)
        obj.meta = meta
        obj.vectors = None
        with open(os.path.join(directory, "chunks.json"), encoding="utf-8") as f:
            obj.chunks = json.load(f)
        obj.dim = 0
        obj.client = chromadb.PersistentClient(path=os.path.join(directory, "chroma"))
        obj.collection = obj.client.get_collection(name="docs")
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