import json
import chunking, config, embedder, rag
from chroma_index import ChromaIndex

cases = {c["id"]: c for c in json.load(open("rag_cases.json", encoding="utf-8"))}
question = cases["D1"]["question"]
docs = chunking.load_documents(config.DOC_DIRS)
chunks = chunking.make_chunks(docs, config.CHUNK_METHOD, config.CHUNK_SIZE, config.CHUNK_OVERLAP, config.WITH_TITLE)
vectors = embedder.embed([c["text"] for c in chunks])

f_top = rag.Index(chunks, vectors).search(question, 1)[0]
c_top = ChromaIndex(chunks, vectors, "chroma_cos", "cosine").search(question, 1)[0]
d_top = ChromaIndex(chunks, vectors, "chroma_default", None).search(question, 1)[0]

print("FAISS, схожість           :", round(f_top["score"], 4), "|", f_top["source"], "#", f_top["chunk"])
print("Chroma cosine, відстань   :", round(c_top["distance"], 4), "|", c_top["source"], "#", c_top["chunk"])
print("Chroma за замовчуванням   :", round(d_top["distance"], 4), "|", d_top["source"], "#", d_top["chunk"])
