SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_rules",
            "description": "Шукає правила перевезення за типом вантажу або обмеженням. "
                           "Використовуй, коли треба дізнатися, чи можна щось відправити "
                           "і за яких умов. Повертає назви знайдених правил одним рядком.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Тип вантажу або обмеження, одне-два слова українською, "
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
            "name": "tariff_info",
            "description": "Шукає тариф у довіднику за назвою міста. "
                           "Використовуй, коли місто призначення вже відоме. "
                           "Повертає ціну за кілограм, термін доставки і мінімальну вартість.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Назва міста українською в називному відмінку",
                    },
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calc_price",
            "description": "Обчислює вартість доставки з урахуванням мінімальної вартості. "
                           "Використовуй ЗАВЖДИ, коли треба порахувати вартість. "
                           "Самостійно нічого не рахуй.",
            "parameters": {
                "type": "object",
                "properties": {
                    "weight": {
                        "type": "number",
                        "description": "Вага посилки в кілограмах",
                    },
                    "price_per_kg": {
                        "type": "number",
                        "description": "Ціна за кілограм, отримана з довідника",
                    },
                    "min_price": {
                        "type": "number",
                        "description": "Мінімальна вартість, отримана з довідника",
                    },
                },
                "required": ["weight", "price_per_kg", "min_price"],
            },
        },
    },
]
