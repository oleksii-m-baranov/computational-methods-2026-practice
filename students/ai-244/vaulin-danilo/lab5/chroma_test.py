"""Перевірка індексу на Chroma для питання D1."""
import chunking
import config
import embedder
import rag
from chroma_index import ChromaIndex

docs = chunking.load_documents(config.DOC_DIRS)
chunks = chunking.make_chunks(docs, config.CHUNK_METHOD, config.CHUNK_SIZE,
                              config.CHUNK_OVERLAP, config.WITH_TITLE)
vectors = embedder.embed([c["text"] for c in chunks])
question = "Яка вартість первинного виготовлення електронного читацького квитка у гривнях?"

faiss_top = rag.Index(chunks, vectors).search(question, 1)[0]
cosine_top = ChromaIndex(chunks, vectors, "chroma_cos", "cosine").search(question, 1)[0]
default_top = ChromaIndex(chunks, vectors, "chroma_default", None).search(question, 1)[0]

print("FAISS, схожість           :", round(faiss_top["score"], 4), f"({faiss_top['source']}#{faiss_top['chunk']})")
print("Chroma cosine, відстань   :", round(cosine_top["distance"], 4), f"({cosine_top['source']}#{cosine_top['chunk']})")
print("Chroma за замовчуванням   :", round(default_top["distance"], 4), f"({default_top['source']}#{default_top['chunk']})")
