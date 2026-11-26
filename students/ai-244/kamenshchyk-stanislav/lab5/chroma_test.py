"""Додаткове завдання: FAISS (у нас numpy-індекс) і Chroma на тих самих чанках і векторах.
Запуск (середовище з Python 3.12 і chromadb): venv\\Scripts\\python.exe chroma_test.py   (результат - logs/chroma_test.txt)"""
import sys

import chunking
import config
import embedder
import rag
from chroma_index import ChromaIndex

sys.stdout = open("logs/chroma_test.txt", "w", encoding="utf-8")   # одразу у файл UTF-8

docs = chunking.load_documents(config.DOC_DIRS)
chunks = chunking.make_chunks(docs, config.CHUNK_METHOD, config.CHUNK_SIZE,
                              config.CHUNK_OVERLAP, config.WITH_TITLE)
vectors = embedder.embed([c["text"] for c in chunks])
question = "Кожні скільки кілометрів пробігу виконується ТО-1?"                                      # вставте текст питання D1

faiss_top = rag.Index(chunks, vectors).search(question, 1)[0]
cosine_top = ChromaIndex(chunks, vectors, "chroma_cos", "cosine").search(question, 1)[0]
default_top = ChromaIndex(chunks, vectors, "chroma_default", None).search(question, 1)[0]

print("FAISS, схожість           :", round(faiss_top["score"], 4))
print("Chroma cosine, відстань   :", round(cosine_top["distance"], 4))
print("Chroma за замовчуванням   :", round(default_top["distance"], 4))
print()
for name, top in [("FAISS", faiss_top), ("Chroma cosine", cosine_top), ("Chroma за замовчуванням", default_top)]:
    print(f"{name:25}: {top['source']}, чанк {top['chunk']}")
