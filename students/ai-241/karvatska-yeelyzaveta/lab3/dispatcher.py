import json

from pydantic import ValidationError
from langfuse import observe

import config
from tools import TOOLS
from arguments import ARGS
from checks import check_meaning


MODEL_ERRORS = [
    "name",
    "permission",
    "syntax",
    "schema",
    "meaning",
]


def format_validation_error(error: ValidationError) -> str:
    """Форматує помилки Pydantic для передавання моделі."""
    messages = []

    for item in error.errors():
        location = ".".join(str(part) for part in item["loc"])
        messages.append(
            f"Поле '{location}': {item['msg']}"
        )

    return "; ".join(messages)


@observe(name="call_tool")
def call_tool(name: str, args_raw: str) -> tuple[str, str]:

    # 1. Перевірка існування інструмента
    if name not in TOOLS:
        return (
            "name",
            f"Інструмента '{name}' не існує."
        )

    # 2. Перевірка дозволу на використання
    if name not in config.ALLOWED:
        return (
            "permission",
            f"Використання інструмента '{name}' заборонено."
        )

    # 3. Перевірка синтаксису JSON
    try:
        args = json.loads(args_raw)
    except (json.JSONDecodeError, TypeError):
        return (
            "syntax",
            "Аргументи мають бути коректним JSON."
        )

    if not isinstance(args, dict):
        return (
            "syntax",
            "Аргументи мають бути JSON-об'єктом."
        )

    # 4. Перевірка структури та типів аргументів
    try:
        validated = ARGS[name].model_validate(args)
        args = validated.model_dump()
    except ValidationError as error:
        return (
            "schema",
            format_validation_error(error)
        )

    # 5. Перевірка змісту аргументів
    meaning_error = check_meaning(name, args)

    if meaning_error:
        return ("meaning", meaning_error)

    # Виконання інструмента після успішних перевірок
    try:
        result = TOOLS[name](**args)
        return ("ok", str(result))

    except Exception as error:
        return (
            "tool_error",
            f"Помилка виконання інструмента: {error}"
        )


def check_response(response):
    """
    Перевіряє повноту відповіді моделі.
    Повертає (рівень, повідомлення) або None.
    """

    if not response.choices:
        return (
            "response",
            "Модель не повернула жодного варіанта відповіді."
        )

    choice = response.choices[0]
    message = choice.message

    if choice.finish_reason == "length":
        return (
            "response",
            "Відповідь обрізана через обмеження довжини."
        )

    if choice.finish_reason == "tool_calls":
        if not message.tool_calls:
            return (
                "response",
                "Модель повідомила про виклик інструмента, "
                "але не повернула його параметри."
            )

        for call in message.tool_calls:
            if (
                not call.function
                or not call.function.name
                or call.function.arguments is None
            ):
                return (
                    "response",
                    "Модель повернула неповний виклик інструмента."
                )

    return None
