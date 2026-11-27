"""Кешування відповідей моделі за хешем запиту.

Навіщо: під час налагодження агента ті самі запитання запускаються десятки разів.
Якщо запит до моделі ідентичний, відповідь береться з файла cache/<хеш>.json -
миттєво і без звернення до сервера.
"""
import hashlib
import json
import os
from openai.types.chat import ChatCompletion

import config
from schemas import SCHEMAS


def cache_key(messages):
    """Хеш запиту: враховує історію, модель, температуру та описи інструментів.

    Якщо змінити системний промпт, назву моделі чи будь-що в історії - хеш буде інший,
    і кеш не поверне застарілу відповідь.
    """
    payload = {
        "model": config.MODEL,
        "temperature": config.TEMPERATURE,
        "messages": messages,
        "tools": SCHEMAS,
    }
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def load_cached(key):
    """Читає збережену відповідь з файла або повертає None, якщо її ще немає."""
    path = f"cache/{key}.json"
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return ChatCompletion.model_validate_json(f.read())


def save_cached(key, response):
    """Записує відповідь сервера в кеш як JSON-рядок."""
    os.makedirs("cache", exist_ok=True)
    with open(f"cache/{key}.json", "w", encoding="utf-8") as f:
        f.write(response.model_dump_json())


def ask_model(client, messages):
    """Викликає сервер або повертає відповідь із кешу. Повертає (відповідь, з_кешу)."""
    if not config.USE_CACHE:
        return client.chat.completions.create(
            model=config.MODEL,
            messages=messages,
            tools=SCHEMAS,
            temperature=config.TEMPERATURE,
        ), False

    key = cache_key(messages)
    cached = load_cached(key)
    if cached is not None:
        return cached, True

    response = client.chat.completions.create(
        model=config.MODEL,
        messages=messages,
        tools=SCHEMAS,
        temperature=config.TEMPERATURE,
    )
    save_cached(key, response)
    return response, False