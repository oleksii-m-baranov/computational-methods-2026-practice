
"""Перевірка кешу на двох однакових запитах."""

import logging
import time

import config
from model import call_model

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cache_test")

config.USE_CACHE = True

messages = [
    {
        "role": "system",
        "content": config.SYSTEM
    },
    {
        "role": "user",
        "content": "Знайди рецепт із рисом."
    }
]

for step in (1, 2):
    started = time.perf_counter()

    response, from_cache = call_model(
        messages,
        step,
        logger
    )

    elapsed = time.perf_counter() - started

    if response is None:
        print("Помилка виклику моделі")
        break

    print(f"\nКрок: {step}")
    print(f"Із кешу: {from_cache}")
    print(f"Час: {elapsed:.4f} с")
    print(f"Вхідних токенів у відповіді: "
          f"{response.usage.prompt_tokens if response.usage else 'немає даних'}")
