import hashlib
import json
from pathlib import Path

from openai.types.chat import ChatCompletion


CACHE_DIR = Path("cache")


def make_key(request):
    payload = json.dumps(
        request,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str
    )

    return hashlib.sha256(
        payload.encode("utf-8")
    ).hexdigest()


def ask_model(client, **request):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    key = make_key(request)
    path = CACHE_DIR / f"{key}.json"

    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)

            response = ChatCompletion.model_validate(data)
            return response, True

        except (OSError, ValueError, TypeError):
            pass

    response = client.chat.completions.create(**request)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(
            response.model_dump(mode="json"),
            file,
            ensure_ascii=False,
            indent=2
        )

    return response, False
