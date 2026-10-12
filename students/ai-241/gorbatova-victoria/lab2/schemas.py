"""Описи інструментів для моделі (JSON Schema)."""

SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_routes",
            "description": (
                "Шукає маршрути вихідного дня за типом відпочинку або назвою місця. "
                "Використовуй, коли користувач описує, куди або як хоче поїхати."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Тип відпочинку або назва місця, одне-два слова українською мовою.",
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
                "Шукає маршрут у довіднику транспорту, повертає вартість проїзду на 1 особу, "
                "час у дорозі та кількість рейсів на день. Використовуй, коли точну назву маршруту вже обрано."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "route": {
                        "type": "string",
                        "description": "Точна назва маршруту українською, як вона записана в довіднику.",
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
                "Використовуй ЗАВЖДИ, коли треба порахувати сумарний бюджет, не рахуй самостійно."
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