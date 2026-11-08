"""Описи інструментів для моделі."""

SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_articles",
            "description": (
                "Шукає статті про догляд за котом за темою або проблемою. "
                "Використовуй, коли користувач описує проблему або ставить "
                "питання про кота. Повертає назви знайдених статей одним рядком."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "Тема або проблема, одне-два слова українською, "
                            "не все питання користувача цілком."
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
            "name": "vaccine_info",
            "description": (
                "Шукає щеплення в довіднику за назвою. "
                "Використовуй, коли назва щеплення вже відома. "
                "Повертає вік першого щеплення, інтервал повторення та ціну."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "vaccine": {
                        "type": "string",
                        "description": (
                            "Назва щеплення в нижньому регістрі, "
                            "як вона записана в довіднику."
                        ),
                    },
                },
                "required": ["vaccine"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calc_food",
            "description": (
                "Обчислює кількість корму на заданий період. "
                "Використовуй завжди, коли треба порахувати корм; "
                "самостійно нічого не рахуй."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "weight_kg": {
                        "type": "number",
                        "description": "Вага кота в кілограмах.",
                    },
                    "grams_per_kg": {
                        "type": "number",
                        "description": (
                            "Норма корму в грамах на кілограм ваги на день; "
                            "якщо користувач не назвав, використовуй 25."
                        ),
                    },
                    "days": {
                        "type": "number",
                        "description": "На скільки днів рахуємо.",
                    },
                },
                "required": ["weight_kg", "grams_per_kg", "days"],
            },
        },
    },
]