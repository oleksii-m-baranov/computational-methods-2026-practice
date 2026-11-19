"""Кеш відповідей моделі за SHA-256 запиту."""
import hashlib
import json
from pathlib import Path
import config

ROOT = Path(__file__).resolve().parent


def make_key(request):
    payload = json.dumps(request, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def ask_model(client, **request):
    if not config.USE_CACHE:
        return client.chat.completions.create(**request), False
    cache_dir = ROOT / "cache"
    cache_dir.mkdir(exist_ok=True)
    path = cache_dir / f"{make_key(request)}.json"
    if path.is_file():
        from openai.types.chat import ChatCompletion
        return ChatCompletion.model_validate_json(path.read_text(encoding="utf-8")), True
    response = client.chat.completions.create(**request)
    path.write_text(response.model_dump_json(), encoding="utf-8")
    return response, False
