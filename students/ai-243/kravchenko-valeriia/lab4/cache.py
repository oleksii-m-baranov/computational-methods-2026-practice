"""Кеш викликів моделі: однаковий запит не надсилається на сервер вдруге."""
import hashlib
import json
import os

from openai.types.chat import ChatCompletion

import config


def make_key(request):
    text = json.dumps(request, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_cache(path):
    with open(path, encoding="utf-8") as f:
        return ChatCompletion.model_validate(json.load(f))


def write_cache(path, response):
    os.makedirs("cache", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(response.model_dump(), f, ensure_ascii=False)


def ask_model(client, **request):
    if not config.USE_CACHE:
        return client.chat.completions.create(**request), False

    path = f"cache/{make_key(request)}.json"
    if os.path.exists(path):
        return read_cache(path), True

    response = client.chat.completions.create(**request)
    write_cache(path, response)
    return response, False