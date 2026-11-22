"""Описи інструментів для моделі."""

SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_plants",
            "description": "Шукає рослини за назвою, умовами догляду або симптомом проблеми. "
                           "Використовуй, коли користувач описує рослину або проблему з нею. "
                           "Повертає назви знайдених рослин одним рядком.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Назва рослини, умова догляду або симптом, "
                                       "одне-два слова українською, "
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
            "name": "fertilizer_info",
            "description": "Шукає рослину в довіднику підживлення. "
                           "Використовуй, коли назва рослини вже відома, наприклад її щойно повернув search_plants. "
                           "Повертає дозу добрива на літр і періодичність у днях.",
            "parameters": {
                "type": "object",
                "properties": {
                    "plant": {
                        "type": "string",
                        "description": "Точна назва рослини, як вона записана в довіднику",
                    },
                },
                "required": ["plant"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calc_dose",
            "description": "Обчислює загальну кількість добрива для горщика заданого об'єму. "
                           "Використовуй завжди, коли треба порахувати дозу; самостійно модель не рахує. "
                           "Повертає кількість добрива в мілілітрах.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pot_liters": {
                        "type": "number",
                        "description": "Об'єм горщика в літрах",
                    },
                    "dose_ml_per_liter": {
                        "type": "number",
                        "description": "Доза на літр, отримана з довідника",
                    },
                },
                "required": ["pot_liters", "dose_ml_per_liter"],
            },
        },
    },
]
