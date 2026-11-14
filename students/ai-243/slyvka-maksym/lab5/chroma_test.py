"""Порівняння результатів пошуку у FAISS та Chroma (додаткове завдання)."""
import json

import chunking
import config
import embedder
import rag
from chroma_index import ChromaIndex

with open("rag_cases.json", encoding="utf-8") as f:
    cases = {c["id"]: c for c in json.load(f)}

docs = chunking.load_documents(config.DOC_DIRS)
chunks = chunking.make_chunks(docs, config.CHUNK_METHOD, config.CHUNK_SIZE,
                              config.CHUNK_OVERLAP, config.WITH_TITLE)
vectors = embedder.embed([c["text"] for c in chunks])
question = cases["D1"]["question"]

faiss_top = rag.Index(chunks, vectors).search(question, 1)[0]
cosine_top = ChromaIndex(chunks, vectors, "chroma_cos", "cosine").search(question, 1)[0]
default_top = ChromaIndex(chunks, vectors, "chroma_default", None).search(question, 1)[0]

print("FAISS, схожість           :", round(faiss_top["score"], 4), "| джерело:", faiss_top["source"], "чанк:", faiss_top["chunk"])
print("Chroma cosine, відстань   :", round(cosine_top["distance"], 4), "| джерело:", cosine_top["source"], "чанк:", cosine_top["chunk"])
print("Chroma за замовчуванням   :", round(default_top["distance"], 4), "| джерело:", default_top["source"], "чанк:", default_top["chunk"])
