SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_books",
            "description": "Шукає книжки за темою, жанром або рівнем складності."
                           "Використовуй, коли користувач описує, яку книжку хоче, але не називає точної назви. "
                           "Повертає назви знайдених книжок одним рядком",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Жанр, тема або рівень складності, "
                                       "одне-два слова українською, "
                                       "не все питання користувача цілком",
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
            "description": "Шукає книжку в довіднику за точною назвою. "
                           "Використовуй ЗАВЖДИ коли точна назва книжки вже відома, "
                           "наприклад її щойно повернув search_books. "
                           "Повертає кількість примірників, термін видачі в днях, штраф за день прострочення",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "точна назва книжки, як вона записана в каталозі",
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
            "description": "Виконує арифметичну дію над двома числами."
                           "Використовую ЗАВЖДИ коли треба щось порахувати; Самостійно нічого не рахуй!",
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["add", "sub", "mul"],
                        "description": "add — додавання, sub — віднімання, mul — множення",
                    },
                    "a": {
                        "type": "number",
                        "description": "Перший операнд",
                    },
                    "b": {
                        "type": "number",
                        "description": "Другий операнд",
                    },
                },
                "required": ["operation", "a", "b"],
            },
        },
    },
]
