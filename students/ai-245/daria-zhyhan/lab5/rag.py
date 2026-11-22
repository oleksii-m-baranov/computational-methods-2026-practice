import hashlib
import json
import os
import urllib.request

import numpy as np

import chunking
import config


def _get_embedding(text, model=None):
    model = model or config.EMBED_MODEL
    url = config.BASE_URL.replace("/v1", "/api/embeddings")
    payload = json.dumps({"model": model, "prompt": text}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["embedding"]


def _load_cache(cache_path):
    if os.path.exists(cache_path):
        with open(cache_path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_cache(cache_path, cache):
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False)


class NumpyIndex:

    def __init__(self, chunks, vectors, model=None):
        self.chunks = chunks
        self.model = model or config.EMBED_MODEL
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self.vectors = (vectors / norms).astype(np.float32)

    def search(self, query, top_k=None, min_score=None):
        top_k = top_k if top_k is not None else config.TOP_K
        min_score = min_score if min_score is not None else config.MIN_SCORE

        q_vec = np.array(_get_embedding(query, self.model), dtype=np.float32)
        norm = np.linalg.norm(q_vec)
        if norm > 0:
            q_vec = q_vec / norm

        scores = self.vectors @ q_vec
        order = np.argsort(scores)[::-1]

        results = []
        for idx in order[:top_k]:
            score = float(scores[idx])
            if score >= min_score:
                item = dict(self.chunks[idx])
                item["score"] = round(score, 4)
                results.append(item)
        return results


def build_index(method=None, size=None, overlap=None, with_title=None):
    method = method if method is not None else config.CHUNK_METHOD
    size = size if size is not None else config.CHUNK_SIZE
    overlap = overlap if overlap is not None else config.CHUNK_OVERLAP
    with_title = with_title if with_title is not None else config.WITH_TITLE

    docs = chunking.load_documents(config.DOC_DIRS)
    chunks = chunking.make_chunks(docs, method, size, overlap, with_title=with_title)

    cache_path = os.path.join(config.INDEX_DIR, "embeddings_cache.json")
    cache = _load_cache(cache_path)
    cache_updated = False

    vectors = []
    for c in chunks:
        key = hashlib.sha256(f"{config.EMBED_MODEL}:{c['text']}".encode("utf-8")).hexdigest()
        if key not in cache:
            cache[key] = _get_embedding(c["text"], config.EMBED_MODEL)
            cache_updated = True
        vectors.append(cache[key])

    if cache_updated:
        _save_cache(cache_path, cache)

    return NumpyIndex(chunks, np.array(vectors, dtype=np.float32), model=config.EMBED_MODEL)


if __name__ == "__main__":
    idx = build_index()
    print(f"Індекс побудовано: {len(idx.chunks)} чанків, розмірність векторів {idx.vectors.shape[1]}")
    for q in ["Скільки годин відстоюється вода?", "Товщина дренажу з керамзиту"]:
        print(f"\nЗапит: {q}")
        for r in idx.search(q, top_k=2):
            print(f"  [{r['source']}#{r['chunk']}] score={r['score']}: {r['text'][:90]}...")