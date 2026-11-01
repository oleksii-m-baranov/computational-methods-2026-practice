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
                        "description": "Тип або місто"
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
                        "description": "Назва міста"
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
                        "description": "Ціна особи"
                    },
                    "people": {
                        "type": "number",
                        "description": "Кількість людей"
                    },
                    "extra": {
                        "type": "number",
                        "description": "Додатково"
                    }
                },
                "required": ["price_per_person", "people", "extra"]
            }
        }
    }
]
