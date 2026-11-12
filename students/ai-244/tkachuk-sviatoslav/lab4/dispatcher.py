"""Ланцюжок перевірок: name → permission → syntax/schema → meaning → tool."""
from langfuse import observe
from pydantic import ValidationError
import config
from arguments import ARGS
from checks import check_meaning
from tools import TOOLS

MODEL_ERRORS = ["name", "permission", "syntax", "schema", "meaning"]


def format_validation_error(error):
    """Що трапилося; які вимоги; що робити далі."""
    lines = ["Помилка: аргументи не пройшли перевірку."]
    for err in error.errors():
        field = '.'.join(str(part) for part in err['loc']) if err['loc'] else 'JSON'
        lines.append(f"Поле {field}: {err['msg']}")
    lines.append("Вкажи всі обов'язкові поля потрібного типу, без зайвих полів і в межах допустимих значень.")
    lines.append("Виправ аргументи і виклич інструмент ще раз.")
    return '\n'.join(lines)


@observe(name="call_tool")
def call_tool(name, args_raw):
    if name not in TOOLS:
        return "name", (f"Помилка: інструмента '{name}' не існує. "
                        f"Доступні: {', '.join(config.ALLOWED)}. "
                        "Виклич доступний інструмент або поясни, що дії немає.")
    if name not in config.ALLOWED:
        return "permission", (f"Помилка: інструмент '{name}' заборонений. "
                              f"Дозволені: {', '.join(config.ALLOWED)}. "
                              "Не повторюй виклик. Поясни користувачу, що запис до ветеринара недоступний.")
    try:
        args = ARGS[name].model_validate_json(args_raw)
    except ValidationError as error:
        level = "syntax" if any(e['type'] == 'json_invalid' for e in error.errors()) else "schema"
        return level, format_validation_error(error)
    problem = check_meaning(name, args)
    if problem is not None:
        return "meaning", problem
    try:
        return "ok", str(TOOLS[name](**args.model_dump()))
    except Exception as error:
        return "tool", (f"Помилка: інструмент '{name}' не спрацював ({error}). "
                        "Не повторюй цей виклик. Повідом користувачу про технічну проблему.")


def check_response(choice):
    if choice.finish_reason == "length":
        return "length", None
    msg = choice.message
    if not msg.tool_calls and msg.content:
        text = msg.content.strip()
        if "<tool_call>" in text or text.startswith("{"):
            return "syntax", ("Помилка: текст схожий на виклик інструмента, але формат неправильний. "
                              "Потрібен структурований tool_calls. Спробуй виклик через API інструментів "
                              "або дай звичайну відповідь без JSON.")
    return None
