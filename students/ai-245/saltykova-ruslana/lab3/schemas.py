import config
from arguments import ARGS

# Текстові описи функцій для моделі
DESCRIPTIONS = {
    "search_recipes": "Шукає рецепти за інгредієнтом, типом страви або способом приготування.",
    "product_info": "Шукає продукт у довіднику за назвою для отримання калорійності та ціни.",
    "scale_amount": "Перераховує кількість інгредієнта на іншу кількість порцій."
}

SCHEMAS = []
for name in config.ALLOWED:
    SCHEMAS.append({
        "type": "function",
        "function": {
            "name": name,
            "description": DESCRIPTIONS[name],
            "parameters": ARGS[name].model_json_schema(),
        }
    })