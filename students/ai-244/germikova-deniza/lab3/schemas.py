
from arguments import ARGS


DESCRIPTIONS = {
    "search_recipes": (
        "Знайти рецепти за назвою, типом страви або інгредієнтами."
    ),
    "product_info": (
        "Отримати харчову цінність продукту та ціну за кілограм "
        "із локального каталогу."
    ),
    "scale_amount": (
        "Перерахувати кількість інгредієнта для іншої кількості порцій."
    ),
}


SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": name,
            "description": DESCRIPTIONS[name],
            "parameters": model.model_json_schema(),
        },
    }
    for name, model in ARGS.items()
]

