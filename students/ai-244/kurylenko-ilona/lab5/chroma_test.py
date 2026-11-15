"""Перевірка та порівняння результатів пошуку FAISS та ChromaDB для додаткового завдання."""
import chunking
import config
import embedder
import rag
from chroma_index import ChromaIndex

docs = chunking.load_documents(config.DOC_DIRS)
chunks = chunking.make_chunks(docs, config.CHUNK_METHOD, config.CHUNK_SIZE,
                              config.CHUNK_OVERLAP, config.WITH_TITLE)
vectors = embedder.embed([c["text"] for c in chunks])
question = "Скільки днів триває плавний перехід на новий раціон кота?"

faiss_top = rag.Index(chunks, vectors).search(question, 1)[0]
cosine_top = ChromaIndex(chunks, vectors, "chroma_cos", "cosine").search(question, 1)[0]
default_top = ChromaIndex(chunks, vectors, "chroma_default", None).search(question, 1)[0]

print("FAISS, схожість           :", round(faiss_top["score"], 4))
print("Chroma cosine, відстань   :", round(cosine_top["distance"], 4))
print("Chroma за замовчуванням   :", round(default_top["distance"], 4))

print("\n--- Перевірка повернених чанків ---")
print(f"FAISS           : source={faiss_top['source']}, chunk={faiss_top['chunk']}")
print(f"Chroma cosine   : source={cosine_top['source']}, chunk={cosine_top['chunk']}")
print(f"Chroma default  : source={default_top['source']}, chunk={default_top['chunk']}")
chunks_match = (
    faiss_top["source"] == cosine_top["source"] == default_top["source"] and
    faiss_top["chunk"] == cosine_top["chunk"] == default_top["chunk"]
)
print(f"Чи збігаються чанки: {'ТАК' if chunks_match else 'НІ'}")
