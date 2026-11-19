"""Додаткове завдання: той самий індекс на FAISS і на Chroma, питання D1."""
import chunking
import config
import embedder
import rag
from chroma_index import ChromaIndex

docs = chunking.load_documents(config.DOC_DIRS)
chunks = chunking.make_chunks(docs, config.CHUNK_METHOD, config.CHUNK_SIZE,
                              config.CHUNK_OVERLAP, config.WITH_TITLE)
vectors = embedder.embed([c["text"] for c in chunks])
question = "Скільки гривень коштує річний абонемент?"      # питання D1

faiss_top = rag.Index(chunks, vectors).search(question, 1)[0]
cosine_top = ChromaIndex(chunks, vectors, "chroma_cos", "cosine").search(question, 1)[0]
default_top = ChromaIndex(chunks, vectors, "chroma_default", None).search(question, 1)[0]

print("FAISS, схожість           :", round(faiss_top["score"], 4))
print("Chroma cosine, відстань   :", round(cosine_top["distance"], 4))
print("Chroma за замовчуванням   :", round(default_top["distance"], 4))

s = faiss_top["score"]
print("\nПеревірка зв'язку чисел:")
print("1 - схожість              :", round(1 - s, 4))
print("2 - 2 * схожість          :", round(2 - 2 * s, 4))

print("\nПерший чанк (файл, номер):")
print("FAISS          :", faiss_top["source"], faiss_top["chunk"])
print("Chroma cosine  :", cosine_top["source"], cosine_top["chunk"])
print("Chroma default :", default_top["source"], default_top["chunk"])
print("Усі три збігаються:",
      (faiss_top["source"], faiss_top["chunk"]) == (cosine_top["source"], cosine_top["chunk"]) == (default_top["source"], default_top["chunk"]))