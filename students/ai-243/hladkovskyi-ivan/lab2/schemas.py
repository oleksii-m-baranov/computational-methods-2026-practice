"""Описи інструментів для моделі."""

SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_routes",
            "description": "Шукає маршрути вихідного дня за типом відпочинку "
                           "або назвою місця. Повертає назви знайдених "
                           "маршрутів одним рядком. Використовуй, коли "
                           "користувач описує, куди або як хоче поїхати.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Тип відпочинку або назва місця: "
                                       "одне-два слова українською "
                                       "(наприклад, «гори» або «море»), "
                                       "не все питання користувача.",
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
            "description": "Шукає маршрут у довіднику транспорту. Повертає "
                           "вартість проїзду на одну особу, час у дорозі "
                           "та кількість рейсів на день. Використовуй, коли "
                           "маршрут уже обрано.",
            "parameters": {
                "type": "object",
                "properties": {
                    "route": {
                        "type": "string",
                        "description": "Точна назва маршруту в називному "
                                       "відмінку, як вона записана "
                                       "в довіднику.",
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
            "description": "Обчислює загальний бюджет поїздки на групу. "
                           "Повертає суму в гривнях. Використовуй ЗАВЖДИ, "
                           "коли треба порахувати бюджет; самостійно не "
                           "рахуй.",
            "parameters": {
                "type": "object",
                "properties": {
                    "price_per_person": {
                        "type": "number",
                        "description": "Вартість проїзду на одну особу, грн.",
                    },
                    "people": {
                        "type": "number",
                        "description": "Кількість людей у групі.",
                    },
                    "extra": {
                        "type": "number",
                        "description": "Додаткові витрати на всю групу, грн; "
                                       "якщо їх немає, передавай 0.",
                    },
                },
                "required": ["price_per_person", "people", "extra"],
            },
        },
    },
]
