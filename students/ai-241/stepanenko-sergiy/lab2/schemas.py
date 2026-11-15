"""Описи інструментів для моделі."""

SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_laptops",
            "description": "Шукає ноутбуки за призначенням або характеристикою "
                           "та повертає назви знайдених моделей одним рядком. "
                           "Використовуй, коли користувач описує, для чого "
                           "потрібен ноутбук, але не називає модель.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Призначення або характеристика ноутбука, "
                                       "одне-два слова українською, "
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
            "name": "laptop_info",
            "description": "Шукає модель ноутбука в довіднику та повертає "
                           "ціну, кількість на складі та гарантію. "
                           "Використовуй, коли модель уже обрано, "
                           "наприклад після search_laptops.",
            "parameters": {
                "type": "object",
                "properties": {
                    "model": {
                        "type": "string",
                        "description": "Точна назва моделі ноутбука, "
                                       "як вона записана в довіднику.",
                    },
                },
                "required": ["model"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calc_installment",
            "description": "Обчислює щомісячний платіж при розстрочці "
                           "та повертає платіж на місяць і загальну суму. "
                           "Використовуй завжди, коли потрібно порахувати "
                           "розстрочку. Не рахуй самостійно.",
            "parameters": {
                "type": "object",
                "properties": {
                    "price": {
                        "type": "number",
                        "description": "Ціна ноутбука в гривнях, "
                                       "отримана з довідника.",
                    },
                    "months": {
                        "type": "number",
                        "description": "Кількість місяців розстрочки.",
                    },
                    "overpay_percent": {
                        "type": "number",
                        "description": "Переплата за весь строк у відсотках. "
                                       "Якщо переплати немає, передавай 0.",
                    },
                },
                "required": ["price", "months", "overpay_percent"],
            },
        },
    },
]