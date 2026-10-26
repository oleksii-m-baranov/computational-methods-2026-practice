"""Описи інструментів для моделі, згенеровані з класів аргументів."""
import config
from arguments import ARGS

DESCRIPTIONS = {
    "search_laptops": "Шукає ноутбуки за запитом. Використовуй для підбору моделі за характеристиками або призначенням.",
    "laptop_info": "Повертає ціну, кількість на складі та гарантію для конкретної моделі ноутбука.",
    "calc_installment": "Розраховує щомісячний платіж при купівлі ноутбука в розстрочку.",
}

SCHEMAS = []
for name in config.ALLOWED:
    SCHEMAS.append({
        "type": "function",
        "function": {
            "name": name,
            "description": DESCRIPTIONS[name],
            "parameters": ARGS[name].model_json_schema(),
        },
    })