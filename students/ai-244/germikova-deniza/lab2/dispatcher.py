"""Диспетчер викликів інструментів кухонного агента."""

import json
from tools import TOOL_FUNCTIONS


def call_tool(name: str, arguments: str) -> str:
    """Викликає потрібний інструмент і повертає результат."""

    if name not in TOOL_FUNCTIONS:
        return (
            f"Помилка: інструмента '{name}' не існує. "
            f"Доступні: {', '.join(TOOL_FUNCTIONS)}"
        )

    try:
        params = json.loads(arguments)
        result = TOOL_FUNCTIONS[name](**params)
        return str(result)

    except json.JSONDecodeError:
        return "Помилка: аргументи не є коректним JSON."

    except TypeError as error:
        return f"Помилка в аргументах: {error}"

    except ValueError as error:
        return f"Помилка значення аргументів: {error}"

    except Exception as error:
        return f"Помилка виконання: {error}"