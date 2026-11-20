

"""Файловий кеш відповідей мовної моделі."""

import hashlib
import json
import os

from openai.types.chat import ChatCompletion


class ModelCache:
    def __init__(self):
        self.cache_dir = "cache"
        os.makedirs(self.cache_dir, exist_ok=True)
        self.hits = 0
        self.misses = 0

    def make_key(self, model, messages, tools, temperature):
        data = {
            "model": model,
            "messages": messages,
            "tools": tools,
            "temperature": temperature,
        }
        serialized = json.dumps(
            data, ensure_ascii=False, sort_keys=True, default=str
        )
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def get(self, key):
        path = os.path.join(self.cache_dir, key + ".json")

        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                response = ChatCompletion.model_validate(json.load(f))
            self.hits += 1
            return response

        self.misses += 1
        return None

    def set(self, key, response):
        path = os.path.join(self.cache_dir, key + ".json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(response.model_dump(), f, ensure_ascii=False)

    def stats(self):
        return {
            "hits": self.hits,
            "misses": self.misses,
            "size": len([
                name for name in os.listdir(self.cache_dir)
                if name.endswith(".json")
            ]),
        }

    def clear(self):
        for name in os.listdir(self.cache_dir):
            if name.endswith(".json"):
                os.remove(os.path.join(self.cache_dir, name))
        self.hits = 0
        self.misses = 0
