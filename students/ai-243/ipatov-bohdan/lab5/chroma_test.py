"""Додаткове завдання: порівняння FAISS і Chroma (cosine та за замовчуванням) на питанні D1."""
import json

import chunking
import config
import embedder
import rag
from chroma_index import ChromaIndex
from utils.lab_logger import custom_logger

logger = custom_logger("chroma_extra", overwrite=True)

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
            f"overlap={config.CHUNK_OVERLAP}, with_title={config.WITH_TITLE}, chunks={len(chunks)}")
logger.info(f"FAISS, схожість           : {round(faiss_top['score'], 4)} | source={faiss_top['source']} chunk={faiss_top['chunk']}")
logger.info(f"Chroma cosine, відстань   : {round(cosine_top['distance'], 4)} | source={cosine_top['source']} chunk={cosine_top['chunk']}")
logger.info(f"Chroma за замовчуванням   : {round(default_top['distance'], 4)} | source={default_top['source']} chunk={default_top['chunk']}")

sim = faiss_top["score"]
logger.info(f"Перевірка формул: 1 - s = {round(1 - sim, 4)} (vs Chroma cosine {round(cosine_top['distance'], 4)}); "
            f"2 - 2*s = {round(2 - 2 * sim, 4)} (vs Chroma default L2^2 {round(default_top['distance'], 4)})")
same_chunk = (faiss_top["source"] == cosine_top["source"] == default_top["source"]
              and faiss_top["chunk"] == cosine_top["chunk"] == default_top["chunk"]
              and faiss_top["text"] == cosine_top["text"] == default_top["text"])
logger.info(f"Чанки збігаються 1-в-1: {same_chunk}")
logger.info(f"Фрагмент знайденого чанка: {faiss_top['text'][:220].replace(chr(10), ' ')}...")
