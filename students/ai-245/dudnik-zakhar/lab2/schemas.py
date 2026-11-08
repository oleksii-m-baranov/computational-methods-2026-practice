SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_exercises",
            "description": "Шукає вправи за групою м'язів або рівнем складності"
                           "Використовуй, користувач описує, що хоче тренувати, але не називає точної назви. "
                           "Повертає назви знайдених вправ одним рядком",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Група м'язів або рівень складності, "
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
            "name": "schedule_info",
            "description": "Шукає заняття в розкладі за назвою. "
                           "Використовуй коли треба дізнатися, "
                           "коли проходить конкретне заняття, "
                           "Повертає день тижня, час початку та ім'я тренера",
            "parameters": {
                "type": "object",
                "properties": {
                    "activity": {
                        "type": "string",
                        "description": "Назва заняття українською в нижньому регістрі",
                    },
                },
                "required": ["activity"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calc_calories",
            "description": "Обчислює витрату калорій за часом, вагою та коефіцієнтом навантаження"
                           "Використовую ЗАВЖДИ коли коли треба порахувати калорії; Самостійно нічого не рахуй!"
                           "Повертає кількість витрачених калорій",
            "parameters": {
                "type": "object",
                "properties": {
                    "minutes": {
                        "type": "number",
                        "description": "Тривалість тренування у хвилинах",
                    },
                    "weight_kg": {
                        "type": "number",
                        "description": "вага людини в кілограмах",
                    },
                    "met": {
                        "type": "number",
                        "description": "Коефіцієнт навантаження; якщо користувач його не назвав, використовуй 5",
                    },
                },
                "required": ["minutes", "weight_kg", "met"],
            },
        },
    },
]
