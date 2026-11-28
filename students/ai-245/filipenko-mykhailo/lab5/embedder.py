
"""Ембединги через Ollama з кешем на диску."""

import hashlib
import json
import os

from openai import OpenAI

import config

client = OpenAI(
    base_url=config.BASE_URL,
    api_key=config.API_KEY
)

CACHE_PATH = os.path.join(
    config.INDEX_DIR,
    "embeddings_cache.json"
)

_cache = None


def _load_cache():
    global _cache

    if _cache is None:
        _cache = {}

        if os.path.exists(CACHE_PATH):
            with open(CACHE_PATH, encoding="utf-8") as f:
                _cache = json.load(f)

    return _cache


def _key(text):
    return hashlib.sha256(
        (config.EMBED_MODEL + "\n" + text).encode("utf-8")
    ).hexdigest()


def embed(texts, batch=16):
    """Повертає список векторів, по одному на кожен текст."""

    cache = _load_cache()

    missing = [
        t for t in dict.fromkeys(texts)
        if _key(t) not in cache
    ]

    for start in range(0, len(missing), batch):
        part = missing[start:start + batch]

        response = client.embeddings.create(
            model=config.EMBED_MODEL,
            input=part
        )

        for text, item in zip(
            part,
            sorted(response.data, key=lambda d: d.index)
        ):
            cache[_key(text)] = item.embedding

    if missing:
        os.makedirs(config.INDEX_DIR, exist_ok=True)

        with open(CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(cache, f)

    return [cache[_key(t)] for t in texts]
