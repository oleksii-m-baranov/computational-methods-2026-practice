"""Додаткове завдання: порівняння FAISS, Chroma cosine і Chroma за замовчуванням."""
import json

import chunking
import config
import embedder
import rag
from chroma_index import ChromaIndex
from utils.lab_logger import custom_logger

logger = custom_logger("extra_chroma", overwrite=True)

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

logger.info(f"Питання D1: {question}")
logger.info(f"Параметри індексу: method={config.CHUNK_METHOD}, size={config.CHUNK_SIZE}, "
            f"overlap={config.CHUNK_OVERLAP}, with_title={config.WITH_TITLE}")
logger.info(f"FAISS, схожість           : {faiss_top['score']:.4f} | {faiss_top['source']}#c{faiss_top['chunk']}")
logger.info(f"Chroma cosine, відстань   : {cosine_top['distance']:.4f} | {cosine_top['source']}#c{cosine_top['chunk']}")
logger.info(f"Chroma за замовчуванням   : {default_top['distance']:.4f} | {default_top['source']}#c{default_top['chunk']}")
logger.info(f"Перевірка формул: 1 - score = {1 - faiss_top['score']:.4f}; "
            f"2 - 2*score = {2 - 2 * faiss_top['score']:.4f}")
logger.info(f"Текст чанка (FAISS): {faiss_top['text']}")
