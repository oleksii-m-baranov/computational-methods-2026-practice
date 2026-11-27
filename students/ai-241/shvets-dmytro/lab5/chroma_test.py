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
question = json.load(open("rag_cases.json", encoding="utf-8"))[0]["question"]                                        # вставте текст питання D1

faiss_top = rag.Index(chunks, vectors).search(question, 1)[0]
cosine_top = ChromaIndex(chunks, vectors, "chroma_cos", "cosine").search(question, 1)[0]
default_top = ChromaIndex(chunks, vectors, "chroma_default", None).search(question, 1)[0]

print("FAISS", faiss_top["score"], faiss_top["source"], faiss_top["chunk"])
print("Chroma cosine", cosine_top["distance"], cosine_top["source"], cosine_top["chunk"])
print("Chroma default", default_top["distance"], default_top["source"], default_top["chunk"])
