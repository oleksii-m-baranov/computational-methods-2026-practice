"""Описи інструментів для моделі."""

SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_service",
            "description": "Шукає регламентні роботи за вузлом автомобіля або пробігом. "
                           "Повертає назви знайдених робіт одним рядком. "
                           "Використовуй, коли користувач описує проблему або називає пробіг.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Вузол автомобіля або пробіг, одне-два слова, "
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
            "name": "price_info",
            "description": "Шукає роботу в прайсі за назвою. Повертає вартість роботи, "
                           "вартість однієї деталі та кількість нормо-годин. "
                           "Використовуй, коли назва роботи вже відома.",
            "parameters": {
                "type": "object",
                "properties": {
                    "service": {
                        "type": "string",
                        "description": "Назва роботи в нижньому регістрі, як вона записана в прайсі",
                    },
                },
                "required": ["service"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calc_total",
            "description": "Обчислює загальну вартість: робота плюс деталі в потрібній кількості. "
                           "Повертає суму в гривнях. Використовуй ЗАВЖДИ, коли треба порахувати "
                           "вартість; самостійно не рахуй.",
            "parameters": {
                "type": "object",
                "properties": {
                    "work_price": {
                        "type": "number",
                        "description": "Вартість роботи, отримана з прайсу",
                    },
                    "part_price": {
                        "type": "number",
                        "description": "Вартість однієї деталі, отримана з прайсу",
                    },
                    "quantity": {
                        "type": "number",
                        "description": "Кількість деталей; якщо користувач не назвав, передавай 1",
                    },
                },
                "required": ["work_price", "part_price", "quantity"],
            },
        },
    },
]
