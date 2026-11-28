"""Ембединги через Ollama з кешем на диску (однаковий текст не рахується вдруге)."""
import hashlib
import json
import os
import urllib.request

import config

CACHE_PATH = os.path.join(config.INDEX_DIR, "embeddings_cache.json")
_cache = None
_opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def _load_cache():
    global _cache
    if _cache is None:
        _cache = {}
        if os.path.exists(CACHE_PATH):
            with open(CACHE_PATH, encoding="utf-8") as f:
                _cache = json.load(f)
    return _cache


def _key(text):
    return hashlib.sha256((config.EMBED_MODEL + "\n" + text).encode("utf-8")).hexdigest()


def embed(texts, batch=16):
    """Повертає список векторів, по одному на кожен текст."""
    cache = _load_cache()
    missing = [t for t in dict.fromkeys(texts) if _key(t) not in cache]
    url = config.BASE_URL.replace("/v1", "/api/embed")
    for start in range(0, len(missing), batch):
        part = missing[start:start + batch]
        payload = json.dumps({"model": config.EMBED_MODEL, "input": part}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with _opener.open(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        for text, vec in zip(part, data["embeddings"]):
            cache[_key(text)] = vec
    if missing:
        os.makedirs(config.INDEX_DIR, exist_ok=True)
        with open(CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(cache, f)
    return [cache[_key(t)] for t in texts]