"""Додаткове завдання: той самий індекс на Chroma."""
import json
import shutil

import chromadb
import numpy as np

import chunking
import config
import embedder
import rag


class ChromaIndex:
    def __init__(self, chunks, vectors, path="chroma_db", space="cosine"):
        client = chromadb.PersistentClient(path=path)
        try:
            client.delete_collection("docs")                  
        except Exception:
            pass
        settings = {"configuration": {"hnsw": {"space": space}}} if space else {}  
        self.collection = client.create_collection("docs", **settings)
        matrix = np.array(vectors, dtype="float32")
        matrix = matrix / np.linalg.norm(matrix, axis=1, keepdims=True)            
        self.collection.add(
            ids=[f"c{i}" for i in range(len(chunks))],
            documents=[c["text"] for c in chunks],
            embeddings=matrix.tolist(),
            metadatas=[{"source": c["source"], "chunk": c["chunk"]} for c in chunks],
        )

    def search(self, query, k=3):
        q = np.array(embedder.embed([query])[0], dtype="float32")
        q = q / np.linalg.norm(q)
        result = self.collection.query(query_embeddings=[q.tolist()], n_results=k)
        return [
            {"distance": float(dist), "source": meta["source"], "chunk": meta["chunk"], "text": text}
            for text, meta, dist in zip(result["documents"][0], result["metadatas"][0], result["distances"][0])
        ]


if __name__ == "__main__":
    docs = chunking.load_documents(config.DOC_DIRS)
    chunks = chunking.make_chunks(
        docs, config.CHUNK_METHOD, config.CHUNK_SIZE,
        config.CHUNK_OVERLAP, config.WITH_TITLE,
    )
    vectors = embedder.embed([c["text"] for c in chunks])

    with open("rag_cases.json", encoding="utf-8") as f:
        cases = {c["id"]: c for c in json.load(f)}
    question = cases["D1"]["question"]

    faiss_top = rag.Index(chunks, vectors).search(question, 1)[0]
    cosine_top = ChromaIndex(chunks, vectors, "chroma_cos", "cosine").search(question, 1)[0]
    default_top = ChromaIndex(chunks, vectors, "chroma_default", None).search(question, 1)[0]

    print("Питання D1                :", question)
    print("FAISS, схожість           :", round(faiss_top["score"], 4))
    print("Chroma cosine, відстань   :", round(cosine_top["distance"], 4))
    print("Chroma за замовчуванням   :", round(default_top["distance"], 4))
    print(
        "Чанки збігаються?         :",
        faiss_top["source"] == cosine_top["source"] == default_top["source"]
        and faiss_top["chunk"] == cosine_top["chunk"] == default_top["chunk"],
        f"({faiss_top['source']}, чанк {faiss_top['chunk']})",
    )

    shutil.rmtree("chroma_cos", ignore_errors=True)
    shutil.rmtree("chroma_default", ignore_errors=True)