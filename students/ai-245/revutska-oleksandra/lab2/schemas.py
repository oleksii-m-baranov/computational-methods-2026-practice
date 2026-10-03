"""Описи інструментів для моделі."""

SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_books",
            "description": (
                "Шукає книжки за темою, жанром або рівнем складності "
                "та повертає назви знайдених книжок одним рядком. "
                "Використовуй, коли користувач описує, яку книжку хоче, "
                "але не називає точної назви."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "Жанр, тема або рівень складності, одне-два "
                            "слова українською, не все питання користувача."
                        ),
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "book_info",
            "description": (
                "Шукає книжку в довіднику за точною назвою та повертає "
                "кількість примірників, термін видачі в днях і штраф "
                "за день прострочення. Використовуй, коли точна назва "
                "книжки вже відома, наприклад її повернув search_books."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": (
                            "Точна назва книжки, як вона записана в каталозі."
                        ),
                    }
                },
                "required": ["title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": (
                "Виконує арифметичну дію над двома числами та повертає "
                "результат. Використовуй завжди, коли треба щось "
                "порахувати; самостійно не рахуй."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["mul", "add", "sub"],
                        "description": (
                            "mul — множення, add — додавання, "
                            "sub — віднімання."
                        ),
                    },
                    "a": {
                        "type": "number",
                        "description": "Перший операнд.",
                    },
                    "b": {
                        "type": "number",
                        "description": "Другий операнд.",
                    },
                },
                "required": ["operation", "a", "b"],
            },
        },
    },
]