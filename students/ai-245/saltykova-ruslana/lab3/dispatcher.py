from langfuse import observe
from pydantic import ValidationError
import config
from arguments import ARGS
from checks import check_meaning
from tools import TOOLS

MODEL_ERRORS = ["name", "permission", "syntax", "schema", "meaning"]


def format_validation_error(error):
    """Збирає з помилки Pydantic коротке повідомлення для моделі."""
    lines = ["Помилка: аргументи не пройшли перевірку."]
    for err in error.errors():
        if err["loc"]:
            field = err["loc"][-1]
        else:
            field = "unknown"
        lines.append(f"Поле {field}: {err['msg']}")
    lines.append("Виправ аргументи і виклич інструмент ще раз.")
    return "\n".join(lines)


@observe(name="call_tool")
def call_tool(name, args_raw):
    """
    Послідовно перевіряє виклик інструмента за рівнями:
    1. name - чи існує інструмент
    2. permission - чи дозволено його викликати
    3. syntax / schema - чи відповідає Pydantic-схемі / JSON
    4. meaning - перевірка змісту
    5. tool - виконання інструмента
    """
    if name not in TOOLS:
        return "name", (
            f"Помилка: інструмента '{name}' не існує. "
            f"Доступні: {', '.join(config.ALLOWED)}. "
            f"Виклич один з доступних або повідом користувачу, що такої дії немає."
        )

    if name not in config.ALLOWED:
        return "permission", (
            f"Помилка: інструмент '{name}' заборонений для використання. "
            f"Доступні: {', '.join(config.ALLOWED)}. "
            f"Не намагайся викликати заборонені дії."
        )

    try:
        args = ARGS[name].model_validate_json(args_raw)

        problem = check_meaning(name, args)
        if problem is not None:
            return "meaning", problem

        result = TOOLS[name](**args.model_dump())
        return "ok", str(result)

    except ValidationError as error:
        level = "schema"
        for err in error.errors():
            if err["type"] == "json_invalid":
                level = "syntax"
        return level, format_validation_error(error)

    except Exception as error:
        return "tool", (
            f"Помилка: інструмент '{name}' зараз не працює ({error}). "
            f"Не повторюй виклик, повідом користувачу."
        )


def check_response(choice):
    """
    Перевіряє відповідь моделі в цілому, до обробки викликів.
    Повертає None, якщо все гаразд, або (рівень, текст).
    """
    if choice.finish_reason == "length":
        return "length", None

    msg = choice.message
    if not msg.tool_calls and msg.content:
        text = msg.content.strip()
        if "tool_calls" in text or text.startswith("("):
            return "syntax", (
                "Твоя відповідь схожа на виклик інструмента, але має неправильний формат. "
                "Виклич інструмент ще раз через механізм інструментів "
                "або дай відповідь користувачу звичайним текстом."
            )
    return None