"""Додаткове завдання: той самий індекс на Chroma."""
import chromadb
import numpy as np

import embedder


class ChromaIndex:
    def __init__(self, chunks, vectors, path="chroma_db", space="cosine"):
        client = chromadb.PersistentClient(path=path)
        try:
            client.delete_collection("docs")                    # щоразу будуємо з нуля
        except Exception:
            pass
        settings = {"configuration": {"hnsw": {"space": space}}} if space else {}   # space=None: значення за замовчуванням
        self.collection = client.create_collection("docs", **settings)
        matrix = np.array(vectors, dtype="float32")
        matrix = matrix / np.linalg.norm(matrix, axis=1, keepdims=True)             # нормалізуємо самі
        self.collection.add(ids=[f"c{i}" for i in range(len(chunks))],
                            documents=[c["text"] for c in chunks],
                            embeddings=matrix.tolist(),
                            metadatas=[{"source": c["source"], "chunk": c["chunk"]} for c in chunks])

    def search(self, query, k=3):
        q = np.array(embedder.embed([query])[0], dtype="float32")
        q = q / np.linalg.norm(q)
        result = self.collection.query(query_embeddings=[q.tolist()], n_results=k)
        return [{"distance": float(dist), "source": meta["source"], "chunk": meta["chunk"], "text": text}
                for text, meta, dist in zip(result["documents"][0], result["metadatas"][0], result["distances"][0])]
