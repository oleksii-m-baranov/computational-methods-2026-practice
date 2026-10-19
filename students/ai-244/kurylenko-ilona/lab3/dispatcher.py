
"""Перевірка і виконання виклику інструмента."""

from langfuse import observe
from pydantic import ValidationError

import config
from arguments import ARGS
from checks import check_meaning
from tools import TOOLS


# Рівні помилок моделі
MODEL_ERRORS = ["name", "permission", "syntax", "schema", "meaning"]


def format_validation_error(error):
    """Збирає з помилки Pydantic коротке повідомлення для моделі."""
    lines = ["Помилка: аргументи не пройшли перевірку."]

    for err in error.errors():
        if err["loc"]:
            field = err["loc"][0]
        else:
            field = "JSON"

        lines.append(f"Поле {field}: {err['msg']}")

    lines.append("Виправ аргументи і виклич інструмент ще раз.")
    return "\n".join(lines)


@observe(name="call_tool")
def call_tool(name, args_raw):

    # 1. Перевірка існування інструмента
    if name not in TOOLS:
        return "name", (
            f"Помилка: інструмента '{name}' не існує. "
            f"Доступні: {', '.join(config.ALLOWED)}. "
            "Виклич один з доступних або повідом користувачу, "
            "що такої дії немає."
        )

    # 2. Перевірка дозволу
    if name not in config.ALLOWED:
        return "permission", (
            f"Помилка: інструмент '{name}' недоступний. "
            "Не повторюй виклик, повідом користувачу, "
            "що ця дія недоступна."
        )

    # 3. Перевірка синтаксису JSON та схеми
    try:
        args = ARGS[name].model_validate_json(args_raw)

    except ValidationError as error:
        level = "schema"

        for err in error.errors():
            if err["type"] == "json_invalid":
                level = "syntax"

        return level, format_validation_error(error)

    # 4. Перевірка змісту аргументів
    problem = check_meaning(name, args)

    if problem is not None:
        return "meaning", problem

    # 5. Виконання інструмента
    try:
        return "ok", str(TOOLS[name](**args.model_dump()))

    except Exception as error:
        return "tool", (
            f"Помилка: інструмент '{name}' зараз не працює ({error}). "
            "Не повторюй виклик, повідом користувачу."
        )


def check_response(choice):
    """Перевіряє відповідь моделі до обробки викликів."""

    if choice.finish_reason == "length":
        return "length", None

    msg = choice.message

    if not msg.tool_calls and msg.content:
        text = msg.content.strip()

        if "<tool_call>" in text or text.startswith("{"):
            return "syntax", (
                "Твоя відповідь схожа на виклик інструмента, "
                "але має неправильний формат. "
                "Виклич інструмент ще раз через механізм інструментів "
                "або дай відповідь користувачу звичайним текстом."
            )

    return None

