"""Додаткове завдання ЛР №5: Chroma зі спільними ембедингами FAISS.

Використовує ту саму нормалізацію векторів та ідентичні чанки.
`space="cosine"`: Chroma повертає косинусну відстань (менше = ближче).
`space=None`: Chroma використовує за замовчуванням l2 (квадрат відстані).
"""
from pathlib import Path
import chromadb
import numpy as np

import embedder


class ChromaIndex:
    def __init__(self, chunks, vectors, path="chroma_db", space="cosine"):
        if not chunks:
            raise ValueError("Не можна створити індекс Chroma з порожніх чанків")
        matrix = np.asarray(vectors, dtype=np.float32)
        if matrix.ndim != 2 or len(matrix) != len(chunks):
            raise ValueError("Число векторів має збігатися з числом чанків")
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        if np.any(norms == 0):
            raise ValueError("Виявлено нульовий ембединг документа")
        matrix = matrix / norms

        client = chromadb.PersistentClient(path=str(Path(path)))
        # Перебудовуємо для чесного порівняння обох режимів з однаковими векторами.
        try:
            client.delete_collection("docs")
        except chromadb.errors.NotFoundError:
            pass
        except ValueError:
            # Старі версії Chroma можуть повертати ValueError для відсутньої колекції.
            pass

        kwargs = ({"configuration": {"hnsw": {"space": space}}} if space else {})
        try:
            self.collection = client.create_collection(name="docs", **kwargs)
        except TypeError:
            if not space:
                raise
            # Chroma 0.x: метрика задавалась через metadata замість configuration.
            self.collection = client.create_collection(name="docs", metadata={"hnsw:space": space})

        self.collection.add(
            ids=[f"c{i}" for i in range(len(chunks))],
            documents=[c["text"] for c in chunks],
            embeddings=matrix.tolist(),
            metadatas=[{"source": c["source"], "chunk": int(c["chunk"])} for c in chunks],
        )

    def search(self, query, k=3):
        vector = np.asarray(embedder.embed([query])[0], dtype=np.float32)
        norm = np.linalg.norm(vector)
        if norm == 0:
            raise ValueError("Нульовий ембединг запиту")
        vector /= norm
        result = self.collection.query(query_embeddings=[vector.tolist()], n_results=k)
        return [
            {"distance": float(distance), "source": meta["source"],
             "chunk": int(meta["chunk"]), "text": text}
            for text, meta, distance in zip(
                result["documents"][0], result["metadatas"][0], result["distances"][0]
            )
        ]
