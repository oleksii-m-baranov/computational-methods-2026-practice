import config
from arguments import ARGS

DESCRIPTIONS = {'search_recipes': 'Шукає рецепти за інгредієнтом, типом страви або способом приготування та повертає назви знайдених страв. Використовуй, коли користувач описує, що хоче приготувати, але не називає точної назви страви.', 'product_info': 'Повертає калорійність продукту на 100 г та ціну за кілограм із довідника. Використовуй для отримання калорійності або вартості конкретного продукту.', 'scale_amount': 'Перераховує кількість інгредієнта на іншу кількість порцій і повертає нову кількість. Завжди використовуй для перерахунку порцій; самостійно не рахуй.'}

DESCRIPTIONS["search_recipes"] = "Шукає рецепти за продуктом або типом страви та повертає повні тексти."
DESCRIPTIONS["scale_amount"] = (
    "Пропорційно перераховує кількість або калорійність: "
    "amount * target_servings / base_servings. Для калорійності amount — ккал "
    "на 100 г, base_servings — 100, target_servings — вага в грамах. "
    "Результат — ккал для заданої ваги. Використовуй для перерахунку."
)
DESCRIPTIONS["scale_amount"] = 'Proportional scaling: amount * target_servings / base_servings. For recipe portions: amount is the original ingredient quantity, base_servings is the original number of portions, target_servings is the requested number of portions; the result has the same units as amount. For calories: amount is kcal per 100 grams, base_servings is 100, target_servings is the requested weight in grams; the result is kcal. Choose the interpretation from the user task.'

SCHEMAS = [{"type": "function", "function": {"name": name,
    "description": DESCRIPTIONS[name], "parameters": ARGS[name].model_json_schema()}}
    for name in config.ALLOWED]
