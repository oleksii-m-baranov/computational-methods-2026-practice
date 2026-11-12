"""Описи інструментів для моделі, згенеровані з класів аргументів."""
import config
from arguments import ARGS

DESCRIPTIONS = {
    "search_laptops": "Шукає ноутбуки в каталозі магазину за призначенням "
                      "або характеристикою. Повертає назви знайдених "
                      "моделей одним рядком через ' | '. "
                      "Використовуй, коли користувач описує, для чого "
                      "йому потрібен ноутбук, але не називає модель.",
    "laptop_info": "Шукає модель ноутбука в довіднику магазину. "
                   "Повертає ціну в гривнях, кількість на складі "
                   "та гарантію в місяцях. Використовуй, коли модель "
                   "уже обрано, наприклад її щойно повернув "
                   "search_laptops.",
    "calc_installment": "Обчислює щомісячний платіж при розстрочці. "
                        "Повертає суму на місяць і загальну суму в гривнях. "
                        "Використовуй ЗАВЖДИ, коли треба порахувати "
                        "розстрочку, самостійно не рахуй.",
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


if __name__ == "__main__":
    import json
    for schema in SCHEMAS:
        print(json.dumps(schema, ensure_ascii=False, indent=2))
