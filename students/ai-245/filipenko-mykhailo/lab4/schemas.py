
import config
from arguments import ARGUMENT_MODELS

SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": name,
            "description": {
                "search_laptops": "Пошук ноутбуків за текстовим запитом",
                "laptop_info": "Отримання ціни, наявності та гарантії ноутбука",
                "calc_installment": "Розрахунок щомісячного платежу за розстрочкою"
            }[name],
            "parameters": ARGUMENT_MODELS[name].model_json_schema()
        }
    }
    for name in config.ALLOWED
]
