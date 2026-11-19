SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_recipes",
            "description": "Шукає рецепти за інгредієнтом, типом страви або способом приготування. Використовуй, коли користувач описує, що хоче приготувати, але не називає точної назви страви.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Інгредієнт, тип страви або спосіб приготування, одне-два слова українською, не все питання користувача цілком."
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
            "description": "Шукає продукт у довіднику за назвою. Використовуй, коли треба дізнатися калорійність або вартість конкретного продукту.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product": {
                        "type": "string",
                        "description": "Назва продукту в називному відмінку однини, як вона записана в довіднику."
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
            "description": "Перераховує кількість інгредієнта на іншу кількість порцій. Використовуй ЗАВЖДИ, коли треба перерахувати порції; самостійно модель не рахує.",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {
                        "type": "number",
                        "description": "Кількість інгредієнта в оригінальному рецепті."
                    },
                    "base_servings": {
                        "type": "number",
                        "description": "На скільки порцій розрахований рецепт."
                    },
                    "target_servings": {
                        "type": "number",
                        "description": "Скільки порцій потрібно."
                    }
                },
                "required": ["amount", "base_servings", "target_servings"]
            }
        }
    }
]