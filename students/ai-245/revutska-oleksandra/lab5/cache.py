
"""Кеш відповідей мовної моделі."""

import copy
import hashlib
import json


class ModelCache:
    """Зберігає відповіді моделі за ключем запиту."""

    def __init__(self):
        self.storage = {}
        self.hits = 0
        self.misses = 0

    def make_key(self, model, messages, tools, temperature):
        """Створює унікальний ключ запиту."""

        data = {
            "model": model,
            "messages": messages,
            "tools": tools,
            "temperature": temperature,
        }

        serialized = json.dumps(
            data,
            ensure_ascii=False,
            sort_keys=True,
            default=str,
        )

        return hashlib.sha256(
            serialized.encode("utf-8")
        ).hexdigest()

    def get(self, key):
        """Повертає відповідь із кешу."""

        if key in self.storage:
            self.hits += 1
            return copy.deepcopy(self.storage[key])

        self.misses += 1
        return None

    def set(self, key, response):
        """Зберігає відповідь моделі."""

        self.storage[key] = copy.deepcopy(response)

    def stats(self):
        """Повертає статистику кешування."""

        return {
            "hits": self.hits,
            "misses": self.misses,
            "size": len(self.storage),
        }

    def clear(self):
        """Очищає кеш і статистику."""

        self.storage.clear()
        self.hits = 0
        self.misses = 0
