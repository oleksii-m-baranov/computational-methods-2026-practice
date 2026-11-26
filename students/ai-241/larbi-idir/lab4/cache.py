"""Кеш викликів моделі: однаковий запит не надсилається на сервер вдруге.

Кеш - це каталог cache/. Кожна відповідь моделі лежить в окремому файлі, ім'я якого
залежить від запиту. Однаковий запит дає однакове ім'я файла, і відповідь береться з нього.
"""
import hashlib
import json
import os

from openai.types.chat import ChatCompletion

import config


def make_key(request):
    """Робить з запиту «відбиток» - довгий рядок із літер і цифр, однаковий для однакових запитів.

    Запит (модель, повідомлення, інструменти, температура) перетворюється на текст JSON,
    а з тексту hashlib.sha256 рахує відбиток. Змінилась хоч одна літера - відбиток інший.
    """
    text = json.dumps(request, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_cache(path):
    """Читає збережену відповідь з файла й повертає її як об'єкт відповіді сервера."""
    with open(path, encoding="utf-8") as f:
        return ChatCompletion.model_validate(json.load(f))


def write_cache(path, response):
    """Зберігає відповідь сервера у файл."""
    os.makedirs("cache", exist_ok=True)        # створюємо каталог cache, якщо його ще немає
    with open(path, "w", encoding="utf-8") as f:
        json.dump(response.model_dump(), f, ensure_ascii=False)


def ask_model(client, **request):
    """Викликає модель (через кеш, якщо він увімкнений).

    Повертає пару: (відповідь, True, якщо відповідь узято з кешу).
    """
    if not config.USE_CACHE:                   # кеш вимкнений: просто звертаємось до сервера
        return client.chat.completions.create(**request), False

    path = f"cache/{make_key(request)}.json"
    if os.path.exists(path):                   # такий запит уже був: беремо відповідь з файла
        return read_cache(path), True

    response = client.chat.completions.create(**request)   # такого запиту ще не було
    write_cache(path, response)                             # запам'ятовуємо відповідь на майбутнє
    return response, False