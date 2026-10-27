
SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_recipes",
            "description": (
                "Знайти рецепти за інгредієнтом, типом страви або способом "
                "приготування. Використовуй, коли користувач просить "
                "запропонувати страву. Передавай короткий пошуковий запит "
                "українською, а не повне запитання."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Короткий пошуковий запит українською"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "product_info",
            "description": (
                "Отримати калорійність на 100 г і ціну за кілограм "
                "із довідника продуктів. Назву передавай точно так, "
                "як вона записана в довіднику."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "product": {
                        "type": "string",
                        "description": "Точна назва продукту українською"
                    }
                },
                "required": ["product"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "scale_amount",
            "description": (
                "Перерахувати кількість інгредієнта для іншої кількості "
                "порцій. Завжди використовуй цей інструмент замість "
                "самостійного обчислення."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {
                        "type": "number",
                        "description": "Початкова кількість інгредієнта"
                    },
                    "base_servings": {
                        "type": "number",
                        "description": "Початкова кількість порцій"
                    },
                    "target_servings": {
                        "type": "number",
                        "description": "Потрібна кількість порцій"
                    }
                },
                "required": [
                    "amount",
                    "base_servings",
                    "target_servings"
                ]
            }
        }
    }
]
