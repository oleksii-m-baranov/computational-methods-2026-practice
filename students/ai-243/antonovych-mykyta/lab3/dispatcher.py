"""Перевірка і виконання виклику інструмента."""

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


def format_validation_error(error):
    """Формує повідомлення про помилку Pydantic."""

    lines = [
        "Помилка: аргументи не пройшли перевірку."
    ]

    for err in error.errors():

        if err["loc"]:
            field = err["loc"][0]
        else:
            field = "JSON"

        lines.append(
            f"Поле {field}: {err['msg']}"
        )

    lines.append(
        "Виправ аргументи і виклич інструмент ще раз."
    )

    return "\n".join(lines)


@observe(name="call_tool")
def call_tool(name, args_raw):
    """Перевіряє та виконує виклик інструмента."""

    # 1. Чи існує інструмент?

    if name not in TOOLS:

        return "name", (
            f"Помилка: інструмента '{name}' не існує. "
            f"Доступні: {', '.join(config.ALLOWED)}. "
            "Виклич один із доступних інструментів "
            "або повідом користувачу, що такої дії немає."
        )

    # 2. Чи дозволено виклик?

    if name not in config.ALLOWED:

        return "permission", (
            f"Помилка: інструмент '{name}' недоступний. "
            "Не повторюй виклик. "
            "Повідом користувачу, що ця дія недоступна."
        )

    # 3. Перевірка синтаксису JSON і схеми

    try:

        args = ARGS[name].model_validate_json(args_raw)

    except ValidationError as error:

        level = "schema"

        for err in error.errors():

            if err["type"] == "json_invalid":
                level = "syntax"

        return level, format_validation_error(error)

    # 4. Перевірка змісту

    problem = check_meaning(name, args)

    if problem is not None:
        return "meaning", problem

    # 5. Виконання інструмента

    try:

        result = TOOLS[name](**args.model_dump())

        return "ok", str(result)

    except Exception as error:

        return "tool", (
            f"Помилка: інструмент '{name}' "
            f"зараз не працює ({error}). "
            "Не повторюй виклик, повідом користувачу."
        )


def check_response(choice):
    """Перевіряє відповідь моделі до обробки викликів."""

    # Обрив відповіді

    if choice.finish_reason == "length":
        return "length", None

    msg = choice.message

    # Зламаний виклик у тексті

    if not msg.tool_calls and msg.content:

        text = msg.content.strip()

        if "<tool_call>" in text or text.startswith("{"):

            return "syntax", (
                "Твоя відповідь схожа на виклик інструмента, "
                "але має неправильний формат. "
                "Виклич інструмент через механізм інструментів "
                "або дай відповідь звичайним текстом."
            )

    return None
