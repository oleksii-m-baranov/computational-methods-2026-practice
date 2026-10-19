"""Описи інструментів для моделі (Варіант 1 — Бібліотека)."""

SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_books",
            "description": (
                "Шукає книжки в каталозі за темою, жанром або рівнем складності. "
                "Використовуй, коли користувач описує, яку книжку хоче, але не називає точної назви."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "Жанр, тема або рівень складності (1-2 слова українською). "
                            "НЕ передавай усе питання користувача цілком."
                        ),
                    },
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
                "Шукає інформацію про книжку в довіднику за її точною назвою. "
                "Повертає кількість примірників, термін видачі та штраф за день. "
                "Використовуй, коли точна назва книжки вже відома (наприклад, її щойно повернув search_books)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Точна назва книжки, як вона записана в каталозі.",
                    },
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
                "Виконує арифметичну дію над двома числами. "
                "Використовуй ЗАВЖДИ, коли треба щось порахувати (наприклад, суму штрафу за кілька днів), "
                "оскільки модель не рахує самостійно."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["mul", "add", "sub"],
                        "description": "Арифметична операція: mul — множення, add — додавання, sub — віднімання.",
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