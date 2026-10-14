"""Автоматичне формування схем інструментів із Pydantic-моделей."""

import config
from arguments import ARGS


DESCRIPTIONS = {
    "search_books": "Пошук книжок за ключовим словом.",
    "book_info": "Отримання інформації про книжку.",
    "calculate": "Виконання арифметичних операцій.",
}


SCHEMAS = []

for name in config.ALLOWED:
    SCHEMAS.append({
        "type": "function",
        "function": {
            "name": name,
            "description": DESCRIPTIONS[name],
            "parameters": ARGS[name].model_json_schema(),
        },
    })