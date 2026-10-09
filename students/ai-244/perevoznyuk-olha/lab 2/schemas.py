SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_routes",
            "description": "Шукає доступні маршрути транспорту за запитом."
                           "Використовууй, коли користувач описує, куди або як хоче поїхати"
                           "Повертає назви знайдених маршрутів одним рядком",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "тип відпочинку або назва місця,"
                        " одне-два слова українською,"
                        " не все питання користувача",
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
            "description": "Шукає маршрут у довіднику транспорту"
                           "Використовууй, коли маршрут уже обрано"
                            "Повертає вартість проїзду на одну особу, час у дорозі та кількість рейсів на день",
            "parameters": {
                "type": "object",
                "properties": {
                    "route": {
                        "type": "string",
                        "description": "точна назва маршруту, як вона записана в довіднику",
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
            "description": "Обчислює загальний бюджет поїздки на групу"
                           "Використовууй завжди, коли треба порахувати бюджет; самостійно модель не рахує"
                           "Повертає суму в гривнях",
            "parameters": {
                "type": "object",
                "properties": {
                    "price_per_person": {
                        "type": "number",
                        "description": "Вартість проїзду на одну особу",
                    },
                    "people": {
                        "type": "number",
                        "description": "Кількість людей у групі",
                    },
                    "extra": {
                        "type": "number",
                        "description": "Додаткові витрати на групу",
                    },
                },
                "required": ["price_per_person", "people", "extra"],
            },
        },
    }
]