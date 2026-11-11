"""Описи інструментів для моделі (JSON Schema) — Варіант 7."""

SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_routes",
            "description": (
                "Шукає маршрути вихідного дня за типом відпочинку або назвою місця. "
                "Використовуй, коли користувач описує, куди або як хоче поїхати. "
                "Повертає назви знайдених маршрутів одним рядком."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Тип відпочинку або назва місця, одне-два слова українською, не все питання користувача цілком.",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "transport_info",
            "description": (
                "Шукає маршрут у довіднику транспорту за точною назвою. "
                "Використовуй ЗАВЖДИ, коли точна назва маршруту вже відома, "
                "наприклад її щойно повернув search_routes. "
                "Повертає вартість проїзду на 1 особу, час у дорозі та кількість рейсів на день."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "route": {
                        "type": "string",
                        "description": "Точна назва маршруту, як вона записана в довіднику.",
                    },
                },
                "required": ["route"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calc_budget",
            "description": (
                "Обчислює загальний бюджет поїздки на групу. "
                "Використовуй ЗАВЖДИ, коли треба порахувати сумарний бюджет; самостійно нічого не рахуй!"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "price_per_person": {
                        "type": "number",
                        "description": "Вартість проїзду на одну особу в один бік (грн).",
                    },
                    "people": {
                        "type": "number",
                        "description": "Кількість людей у групі.",
                    },
                    "extra": {
                        "type": "number",
                        "description": "Додаткові витрати на всю групу (грн). Якщо їх немає, передавай 0.",
                    },
                },
                "required": ["price_per_person", "people", "extra"],
            },
        },
    },
]