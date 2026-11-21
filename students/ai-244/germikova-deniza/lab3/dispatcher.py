
"""Перевірка та виконання викликів інструментів."""

import json

from langfuse import observe
from pydantic import ValidationError

import config
from arguments import ARGS
from checks import check_meaning

from tools import (
    search_recipes,
    product_info,
    scale_amount,
    place_order,
)


TOOLS = {
    "search_recipes": search_recipes,
    "product_info": product_info,
    "scale_amount": scale_amount,
    "place_order": place_order,
}


MODEL_ERRORS = {
    "name",
    "permission",
    "syntax",
    "schema",
    "meaning",
}


def format_validation_error(error):
    """Формує зрозуміле повідомлення про помилку для моделі."""

    lines = [
        "Помилка: аргументи не пройшли перевірку."
    ]

    for err in error.errors():
        field = ".".join(
            str(part) for part in err["loc"]
        ) or "JSON"

        lines.append(
            f"Поле {field}: {err['msg']}"
        )

    lines.append(
        "Перевір типи, обов'язкові поля та допустимі значення."
    )

    lines.append(
        "Виправ аргументи і виклич інструмент ще раз."
    )

    return "\n".join(lines)


@observe(name="call_tool")
def call_tool(name: str, arguments: str) -> tuple[str, str]:
    """
    Перевіряє виклик інструмента.

    Повертає:
    - рівень перевірки;
    - результат або повідомлення про помилку.
    """

    # 1. Перевірка існування інструмента.
    if name not in TOOLS:
        return "name", (
            f"Помилка: інструмента '{name}' не існує. "
            f"Доступні інструменти: {', '.join(config.ALLOWED)}. "
            "Виклич один із доступних інструментів "
            "або повідом користувачу, що така дія недоступна."
        )

    # 2. Перевірка дозволу.
    if name not in config.ALLOWED:
        return "permission", (
            f"Помилка: виклик інструмента '{name}' заборонено. "
            "Ця дія недоступна для кулінарного агента. "
            "Не повторюй виклик і повідом користувачу "
            "про неможливість виконати дію."
        )

    # 3. Перевірка синтаксису JSON.
    try:
        params = json.loads(arguments)

    except (json.JSONDecodeError, TypeError):
        return "syntax", (
            "Помилка: некоректний JSON аргументів. "
            "Аргументи повинні бути правильно сформованим "
            "JSON-об'єктом. "
            "Виправ синтаксис і повтори виклик інструмента."
        )

    # 4. Перевірка структури JSON.
    if not isinstance(params, dict):
        return "schema", (
            "Помилка: неправильна структура аргументів. "
            "Очікується JSON-об'єкт із полями інструмента. "
            "Виправ аргументи і повтори виклик."
        )

    # 5. Валідація аргументів через Pydantic.
    try:
        validated = ARGS[name].model_validate(params)

    except ValidationError as error:
        return "schema", format_validation_error(error)

    params = validated.model_dump()

    # 6. Семантична перевірка аргументів.
    try:
        valid, message = check_meaning(name, params)

    except Exception as error:
        return "tool", (
            "Помилка: не вдалося виконати перевірку змісту "
            f"аргументів ({error}). "
            "Не повторюй той самий виклик без змін."
        )

    if not valid:
        return "meaning", (
            f"Помилка: {message} "
            "Значення має відповідати даним локального каталогу. "
            "Перевір і виправ аргумент або повідом користувачу, "
            "що відповідних даних немає."
        )

    # 7. Виконання інструмента.
    try:
        result = TOOLS[name](**params)
        return "ok", str(result)

    except Exception as error:
        return "tool", (
            f"Помилка: інструмент '{name}' не працює ({error}). "
            "Не повторюй виклик без змін, "
            "повідом користувачу про проблему."
        )


def check_response(choice):
    """Перевіряє відповідь моделі на обрізання та помилки формату."""

    message = choice.message
    content = message.content or ""

    # Перевірка обрізаної відповіді.
    if choice.finish_reason == "length":
        return (
            False,
            "Відповідь моделі обрізана через обмеження довжини."
        )

    # Перевірка некоректного текстового виклику.
    broken_markers = (
        "<tool_call>",
        "</tool_call>",
        "<function=",
    )

    if not message.tool_calls and any(
        marker in content.lower()
        for marker in broken_markers
    ):
        return (
            False,
            "Відповідь містить некоректний текст виклику "
            "інструмента. Використай правильний механізм "
            "виклику інструментів."
        )

    return True, "ok"
