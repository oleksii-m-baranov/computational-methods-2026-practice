SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_routes",
            "description": "Шукає маршрути вихідного дня за типом відпочинку або назвою місця. Використовуй, коли користувач шукає цікаві місця, тури чи маршрути для відпочинку.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Ключове слово, тип відпочинку або назва місця українською"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "transport_info",
            "description": "Шукає маршрут у довіднику транспорту (вартість, час у дорозі, рейси). Використовуй, коли потрібно дізнатися інформацію про транспорт для конкретного маршруту.",
            "parameters": {
                "type": "object",
                "properties": {
                    "route": {
                        "type": "string",
                        "description": "Назва маршруту або міста українською"
                    }
                },
                "required": ["route"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calc_budget",
            "description": "Обчислює загальний бюджет поїздки на групу. Використовуй для розрахунку загальної вартості поїздки.",
            "parameters": {
                "type": "object",
                "properties": {
                    "price_per_person": {
                        "type": "number",
                        "description": "Вартість поїздки на одну особу"
                    },
                    "people": {
                        "type": "number",
                        "description": "Кількість людей у групі"
                    },
                    "extra": {
                        "type": "number",
                        "description": "Додаткові витрати"
                    }
                },
                "required": ["price_per_person", "people", "extra"]
            }
        }
    }
]