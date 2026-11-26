import chunking
import config
import embedder
import rag
from chroma_index import ChromaIndex

docs = chunking.load_documents(config.DOC_DIRS)
chunks = chunking.make_chunks(docs, config.CHUNK_METHOD, config.CHUNK_SIZE,
                              config.CHUNK_OVERLAP, config.WITH_TITLE)
vectors = embedder.embed([c["text"] for c in chunks])
import json
question = next(c["question"] for c in json.load(open("rag_cases.json", encoding="utf-8")) if c["id"] == "D1")                                        # вставте текст питання D1

faiss_top = rag.Index(chunks, vectors).search(question, 1)[0]
cosine_top = ChromaIndex(chunks, vectors, "chroma_cos", "cosine").search(question, 1)[0]
default_top = ChromaIndex(chunks, vectors, "chroma_default", None).search(question, 1)[0]

print("FAISS, схожість           :", round(faiss_top["score"], 4))
print("Chroma cosine, відстань   :", round(cosine_top["distance"], 4))
print("Chroma за замовчуванням   :", round(default_top["distance"], 4))
for name, item in [("FAISS",faiss_top),("Chroma cosine",cosine_top),("Chroma default",default_top)]:
    print(name, item["source"], item["chunk"])
