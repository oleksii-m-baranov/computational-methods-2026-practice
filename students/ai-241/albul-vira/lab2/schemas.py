"""Описи інструментів для моделі (покращені підказки)."""

SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_books",
            "description": (
                "ОБОВ'ЯЗКОВО викликай першим, якщо точна назва книжки невідома. "
                "Шукає книжки за жанром, темою або рівнем складності. "
                "Повертає точні назви книжок."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "Передавай strictly ОДНЕ слово українською: "
                            "або жанр ('фантастика'), або тему ('алгоритми'), "
                            "або складність ('легкий'). Ніколи не об'єднуй кілька слів!"
                            "Передавай корінь одного слова українською (наприклад: 'алгоритм', 'фантаст', 'легк'). Не додавай закінчень!"
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
                "Шукає книжку в довіднику. Використовуй ТІЛЬКИ після того, як search_books "
                "повернув точну назву книжки. НІКОЛИ не вигадуй назву самостійно!"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Точна назва книжки, яка була отримана з search_books",
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
                "Виконує арифметичні обчислення (множення, додавання, віднімання). "
                "Використовуй ЗАВЖДИ для підрахунку штрафу (дні * штраф_за_день)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["mul", "add", "sub"],
                        "description": "mul — множення, add — додавання, sub — віднімання",
                    },
                    "a": {
                        "type": "number",
                        "description": "Перше число (наприклад, кількість днів)",
                    },
                    "b": {
                        "type": "number",
                        "description": "Друге число (наприклад, ставка штрафу)",
                    },
                },
                "required": ["operation", "a", "b"],
            },
        },
    },
]