"""Перевірка і виконання виклику інструмента."""
from pydantic import ValidationError

try:
    from langfuse import observe
except ImportError:
    def observe(*args, **kwargs):
        def decorator(f):
            return f
        return decorator

import config
from arguments import ARGS
from checks import check_meaning
from tools import TOOLS

# Рівні помилок моделі
MODEL_ERRORS = ["name", "permission", "syntax", "schema", "meaning"]


def format_validation_error(error: ValidationError) -> str:
    """Збирає з помилки Pydantic повідомлення для моделі з трьох частин."""
    lines = ["Помилка: аргументи не пройшли перевірку."]
    for err in error.errors():
        field = err["loc"][0] if err["loc"] else "JSON"
        lines.append(f"Поле {field}: {err['msg']}")
    lines.append("Виправ аргументи і виклич інструмент ще раз.")
    return "\n".join(lines)


@observe(name="call_tool")
def call_tool(name: str, args_raw: str):
    """Ланцюжок перевірок виклику інструмента.
    Повертає (level, message_or_result)."""
    # 1. Рівень name: чи існує інструмент взагалі
    if name not in TOOLS and name not in ARGS:
        return "name", (
            f"Помилка: інструмента '{name}' не існує. "
            f"Доступні: {', '.join(config.ALLOWED)}. "
            "Виклич один з доступних або повідом користувачу, що такої дії немає."
        )

    # 2. Рівень permission: чи дозволено його викликати агенту
    if name not in config.ALLOWED:
        return "permission", (
            f"Помилка: інструмент '{name}' недоступний для виклику. "
            "Не повторюй виклик, повідом користувачу, що ця дія недоступна."
        )

    # 3. Рівень syntax та schema: Pydantic валідація
    try:
        args = ARGS[name].model_validate_json(args_raw)
    except ValidationError as error:
        level = "schema"
        for err in error.errors():
            if err["type"] == "json_invalid":
                level = "syntax"
        return level, format_validation_error(error)

    # 4. Рівень meaning: перевірка змісту для предметної області
    problem = check_meaning(name, args)
    if problem is not None:
        return "meaning", problem

    # 5. Рівень tool / ok: безпосереднє виконання
    try:
        return "ok", str(TOOLS[name](**args.model_dump()))
    except Exception as error:
        return "tool", (
            f"Помилка: інструмент '{name}' зараз не працює ({error}). "
            "Не повторюй виклик, повідом користувачу."
        )


def check_response(choice):
    """Перевіряє відповідь моделі в цілому, до обробки викликів."""
    if choice.finish_reason == "length":
        return "length", None

    msg = choice.message
    if not msg.tool_calls and msg.content:
        text = msg.content.strip()
        if "<tool_call>" in text or (text.startswith("{") and "}" in text and "query" in text):
            return "syntax", (
                "Твоя відповідь схожа на виклик інструмента, але має неправильний формат. "
                "Виклич інструмент ще раз через механізм інструментів "
                "або дай відповідь користувачу звичайним текстом."
            )
    return None
