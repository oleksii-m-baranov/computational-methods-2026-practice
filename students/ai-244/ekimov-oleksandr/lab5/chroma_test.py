"""Порівняння FAISS та Chroma (cosine і за замовчуванням) на питанні D1."""
import json

import chunking
import config
import embedder
import rag
from chroma_index import ChromaIndex

with open("rag_cases.json", encoding="utf-8") as f:
    cases = json.load(f)

d1_case = next(c for c in cases if c["id"] == "D1")
question = d1_case["question"]

docs = chunking.load_documents(config.DOC_DIRS)
chunks = chunking.chunk_documents(
    docs,
    method=config.CHUNK_METHOD,
    chunk_size=config.CHUNK_SIZE,
    chunk_overlap=config.CHUNK_OVERLAP,
    with_title=config.WITH_TITLE,
)
vectors = embedder.embed([c["text"] for c in chunks])

faiss_top = rag.Index(chunks, vectors).search(question, 1)[0]
cosine_top = ChromaIndex(chunks, vectors, "chroma_cos", "cosine").search(question, 1)[0]
default_top = ChromaIndex(chunks, vectors, "chroma_default", None).search(question, 1)[0]

print("Питання D1:", question)
print("FAISS, схожість           :", round(faiss_top["score"], 4), "| джерело:", faiss_top["source"])
print("Chroma cosine, відстань   :", round(cosine_top["distance"], 4), "| джерело:", cosine_top["source"])
print("Chroma за замовчуванням   :", round(default_top["distance"], 4), "| джерело:", default_top["source"])