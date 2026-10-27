"""Диспетчер інструментів із багаторівневою перевіркою."""

import json

from langfuse import observe
from pydantic import ValidationError

import config
from arguments import ARGS
from checks import check_meaning
from tools import TOOLS


MODEL_ERRORS = [
    "name",
    "permission",
    "syntax",
    "schema",
    "meaning",
]


@observe(name="call_tool")
def call_tool(name: str, args_raw: str) -> tuple[str, str]:
    """Повертає рівень перевірки та текст результату."""

    # 1. Існування інструмента
    if name not in TOOLS:
        return "name", (
            f"Помилка: інструмента '{name}' не існує. "
            f"Доступні: {', '.join(config.ALLOWED)}. "
            "Вибери доступний інструмент."
        )

    # 2. Перевірка дозволу
    if name not in config.ALLOWED:
        return "permission", (
            f"Помилка: інструмент '{name}' заборонений. "
            "Не повторюй виклик. "
            "Повідом користувачу про обмеження."
        )

    # 3–4. Перевірка JSON і схеми Pydantic
    try:
        args = ARGS[name].model_validate_json(args_raw)

    except ValidationError as error:
        errors = error.errors()

        if any(
            item["type"] == "json_invalid"
            for item in errors
        ):
            return "syntax", (
                "Помилка: аргументи не є коректним JSON. "
                "Виправ синтаксис JSON."
            )

        return "schema", (
            "Помилка перевірки аргументів: "
            f"{error}. "
            "Виправ аргументи відповідно до схеми."
        )

    except (TypeError, ValueError) as error:
        return "syntax", (
            f"Помилка формату аргументів: {error}"
        )

    # 5. Перевірка змісту
    meaning_error = check_meaning(name, args)

    if meaning_error is not None:
        return "meaning", meaning_error

    # 6. Виконання інструмента
    try:
        result = TOOLS[name](**args.model_dump())
        return "ok", str(result)

    except Exception as error:
        return "tool", (
            f"Помилка виконання інструмента: {error}"
        )