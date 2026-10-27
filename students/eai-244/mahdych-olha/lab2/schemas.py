"""Описи інструментів для варіанта 2."""
SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_recipes",
            "description": "Шукає рецепти за інгредієнтом, типом страви або способом приготування та повертає назви знайдених страв. Використовуй, коли користувач описує, що хоче приготувати, але не називає точної назви страви.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Інгредієнт, тип страви або спосіб приготування: одне-два слова українською, не все питання користувача."
                    }
                },
                "required": [
                    "query"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "product_info",
            "description": "Повертає калорійність продукту на 100 г та ціну за кілограм із довідника. Використовуй для отримання калорійності або вартості конкретного продукту.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product": {
                        "type": "string",
                        "description": "Назва продукту в називному відмінку однини, як у довіднику."
                    }
                },
                "required": [
                    "product"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "scale_amount",
            "description": "Перераховує кількість інгредієнта на іншу кількість порцій і повертає нову кількість. Завжди використовуй для перерахунку порцій; самостійно не рахуй.",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {
                        "type": "number",
                        "description": "Кількість інгредієнта в оригінальному рецепті."
                    },
                    "base_servings": {
                        "type": "number",
                        "description": "Кількість порцій в оригінальному рецепті."
                    },
                    "target_servings": {
                        "type": "number",
                        "description": "Потрібна кількість порцій."
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
