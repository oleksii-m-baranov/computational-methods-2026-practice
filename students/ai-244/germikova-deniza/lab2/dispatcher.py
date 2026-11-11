"""Диспетчер викликів інструментів кухонного агента."""

import json
from tools import search_recipes, product_info, scale_amount

TOOL_FUNCTIONS = {
    "search_recipes": search_recipes,
    "product_info": product_info,
    "scale_amount": scale_amount,
}


def call_tool(name: str, arguments: str) -> str:
    """Викликає потрібний інструмент і повертає результат."""
    if name not in TOOL_FUNCTIONS:
        return f"Помилка: інструмент '{name}' не існує."

    try:
        params = json.loads(arguments)
        result = TOOL_FUNCTIONS[name](**params)
        return str(result)
    except (json.JSONDecodeError, TypeError, ValueError) as error:
        return f"Помилка виклику інструмента: {error}"