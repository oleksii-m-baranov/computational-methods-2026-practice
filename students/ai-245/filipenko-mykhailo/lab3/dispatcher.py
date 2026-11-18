"""Перевірка та виконання інструментів AI-агента. ЛР3."""

import json

from langfuse import observe
from pydantic import ValidationError

import config
from arguments import ARGUMENT_MODELS
from checks import check_meaning
from tools import TOOLS


MODEL_ERRORS = {
    "name",
    "permission",
    "syntax",
    "schema",
    "meaning"
}


@observe(name="call_tool")
def call_tool(name, arguments, context=None):
    """
    Перевіряє виклик інструмента перед виконанням.

    context містить підтверджені дані, які агент
    отримав під час поточного завдання.

    Повертає (рівень_результату, повідомлення).
    """

    if context is None:
        context = {}

    # 2. Перевірка забороненої дії
    if name == "place_order":
        return (
            "permission",
            "Помилка: оформлення замовлення заборонено. "
            "Ця дія недоступна. Не повторюй виклик, "
            "повідом користувачу про обмеження."
        )

    # 3. Перевірка існування інструмента
    if name not in TOOLS:
        return (
            "name",
            f"Помилка: інструмента '{name}' не існує. "
            f"Доступні: {', '.join(config.ALLOWED)}. "
            "Виклич доступний інструмент або повідом користувачу, "
            "що такої дії немає."
        )

    # 4. Перевірка дозволів
    if name not in config.ALLOWED:
        return (
            "permission",
            f"Помилка: інструмент '{name}' заборонений. "
            "Ця дія недоступна. Не повторюй виклик, "
            "повідом користувачу про обмеження."
        )

    # 5. Перевірка синтаксису JSON
    try:
        data = (
            json.loads(arguments)
            if isinstance(arguments, str)
            else arguments
        )

    except (json.JSONDecodeError, TypeError, ValueError) as error:
        return (
            "syntax",
            f"Помилка: некоректний JSON ({error}). "
            "Аргументи мають бути правильним JSON-об'єктом. "
            "Виправ синтаксис і повтори виклик."
        )

    # 6. Перевірка схеми через Pydantic
    try:
        model_class = ARGUMENT_MODELS[name]
        validated = model_class.model_validate(data)
        data = validated.model_dump()

    except (ValidationError, KeyError, TypeError, ValueError) as error:
        return (
            "schema",
            f"Помилка: аргументи не відповідають схемі ({error}). "
            "Використовуй лише дозволені поля та правильні типи. "
            "Виправ аргументи й повтори виклик."
        )

    # 7. Семантична перевірка з урахуванням контексту
    try:
        valid, message = check_meaning(
            name,
            data,
            context=context
        )

    except Exception as error:
        return (
            "meaning",
            f"Помилка змістової перевірки: {error}. "
            "Перевір значення аргументів і повтори виклик."
        )

    if not valid:
        return (
            "meaning",
            f"Помилка: {message} "
            "Виправ аргументи та повтори виклик."
        )

    # 8. Виконання оригінального інструмента ЛР2
    try:
        result = TOOLS[name](**data)
        return "ok", str(result)

    except Exception as error:
        return (
            "tool",
            f"Помилка: інструмент '{name}' не спрацював ({error}). "
            "Не повторюй виклик автоматично. "
            "Повідом користувачу, що дія зараз недоступна."
        )


def check_response(response):
    """Перевіряє структуру відповіді мовної моделі."""

    # 9. Перевірка наявності відповіді
    if not response.choices:
        return (
            "response",
            "Модель не повернула відповіді."
        )

    choice = response.choices[0]
    message = choice.message

    # 10. Перевірка ліміту токенів
    if choice.finish_reason == "length":
        return "length", None

    # 11. Перевірка структури викликів інструментів
    if message.tool_calls:
        for call in message.tool_calls:

            if not call.function or not call.function.name:
                return (
                    "syntax",
                    "Помилка: некоректний виклик інструмента. "
                    "Повтори виклик у правильному форматі."
                )

            if not isinstance(call.function.arguments, str):
                return (
                    "syntax",
                    "Помилка: аргументи мають бути JSON-рядком. "
                    "Виправ формат і повтори виклик."
                )

    # 12. Перевірка неправильного tool calling
    if not message.tool_calls and message.content:
        content = message.content.strip()

        if "<tool_call>" in content or content.startswith("{"):
            return (
                "syntax",
                "Помилка: відповідь схожа на неправильно оформлений "
                "виклик інструмента. Використай механізм tool calling "
                "або дай звичайну текстову відповідь."
            )

    return "ok", "OK"
