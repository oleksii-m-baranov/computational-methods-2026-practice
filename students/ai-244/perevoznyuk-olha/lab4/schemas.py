import config
from arguments import ARGS

DESCRIPTIONS = {
    "search_routes": "Шукає доступні маршрути транспорту за запитом."   
                    "Використовууй, коли користувач описує, куди або як хоче поїхати"
                    "Повертає назви знайдених маршрутів одним рядком",
    "transport_info": "Шукає маршрут у довіднику транспорту"
                      "Використовууй, коли маршрут уже обрано"
                      "Повертає вартість проїзду на одну особу, час у дорозі та кількість рейсів на день",
    "calc_budget": "Обчислює загальний бюджет поїздки на групу"
                   "Використовууй завжди, коли треба порахувати бюджет; самостійно модель не рахує"
                   "Повертає суму в гривнях"
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