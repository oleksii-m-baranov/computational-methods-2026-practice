
"""Дисковий кеш відповідей Ollama."""

import hashlib
import json
from pathlib import Path

CACHE_DIR = Path("cache")


def make_key(model, messages, tools, temperature):
    """Формує стабільний ключ для запиту."""

    request = {
        "model": model,
        "messages": messages,
        "tools": tools,
        "temperature": temperature,
    }

    raw = json.dumps(
        request,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str
    )

    return hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()


def get_cached(key):
    """Читає відповідь із кешу."""

    path = CACHE_DIR / f"{key}.json"

    if not path.exists():
        return None

    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def save_cached(key, response):
    """Зберігає відповідь у кеш."""

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    path = CACHE_DIR / f"{key}.json"

    with path.open("w", encoding="utf-8") as f:
        json.dump(
            response.model_dump(mode="json"),
            f,
            ensure_ascii=False,
            indent=2
        )
