"""Описи інструментів для моделі."""

SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_laptops",
            "description": "Шукає ноутбуки за призначенням або характеристикою. "
                           "Використовуй, коли користувач описує, для чого потрібен ноутбук, "
                           "але не називає конкретну модель.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Призначення або характеристика, одне-два слова українською, "
                                       "наприклад 'навчання', 'ігри', 'програмування'. Не все питання користувача.",
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
            "description": "Шукає модель у довіднику та повертає ціну, кількість на складі та гарантію. "
                           "Використовуй, коли модель уже обрано або її щойно повернув пошук.",
            "parameters": {
                "type": "object",
                "properties": {
                    "model": {
                        "type": "string",
                        "description": "Точна назва моделі латиницею, як вона записана в довіднику (наприклад, 'StudyBook 14').",
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
            "description": "Обчислює щомісячний платіж при розстрочці та загальну суму. "
                           "Використовуй ЗАВЖДИ, коли треба порахувати розстрочку, не рахуй самостійно.",
            "parameters": {
                "type": "object",
                "properties": {
                    "price": {
                        "type": "number",
                        "description": "Ціна товару в гривнях, отримана з довідника.",
                    },
                    "months": {
                        "type": "number",
                        "description": "Кількість місяців розстрочки.",
                    },
                    "overpay_percent": {
                        "type": "number",
                        "description": "Переплата за весь строк у відсотках. Якщо переплати немає, передавай 0.",
                    },
                },
                "required": ["price", "months", "overpay_percent"],
            },
        },
    },
]