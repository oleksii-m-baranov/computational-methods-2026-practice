"""Додаткове завдання: той самий індекс на FAISS і Chroma, перший результат для питання D1."""
import json

import chunking
import config
import embedder
import rag
from chroma_index import ChromaIndex

docs = chunking.load_documents(config.DOC_DIRS)
chunks = chunking.make_chunks(docs, config.CHUNK_METHOD, config.CHUNK_SIZE,
                              config.CHUNK_OVERLAP, config.WITH_TITLE)
vectors = embedder.embed([c["text"] for c in chunks])
with open("rag_cases.json", encoding="utf-8") as f:
    question = {c["id"]: c for c in json.load(f)}["D1"]["question"]   # текст питання D1
print("Питання D1:", question)

faiss_top = rag.Index(chunks, vectors).search(question, 1)[0]
cosine_top = ChromaIndex(chunks, vectors, "chroma_cos", "cosine").search(question, 1)[0]
default_top = ChromaIndex(chunks, vectors, "chroma_default", None).search(question, 1)[0]

print("FAISS, схожість           :", round(faiss_top["score"], 4))
print("Chroma cosine, відстань   :", round(cosine_top["distance"], 4))
print("Chroma за замовчуванням   :", round(default_top["distance"], 4))
print("Чанки: FAISS", (faiss_top["source"], faiss_top["chunk"]), "| Chroma cosine",
      (cosine_top["source"], cosine_top["chunk"]), "| Chroma default", (default_top["source"], default_top["chunk"]))
