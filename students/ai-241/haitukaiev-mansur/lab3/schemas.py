"""Описи інструментів для моделі, згенеровані з класів аргументів."""
import config
from arguments import ARGS

DESCRIPTIONS = {
    "search_exercises": "Шукає вправи за групою м'язів або рівнем складності. "
                        "Використовуй, коли користувач описує, що хоче тренувати.",
    "schedule_info": "Шукає заняття в розкладі за назвою. "
                     "Використовуй, коли треба дізнатися, коли проходить конкретне заняття.",
    "calc_calories": "Обчислює витрату калорій за часом, вагою та коефіцієнтом навантаження. "
                     "Використовуй ЗАВЖДИ, коли треба порахувати калорії; самостійно модель не рахує.",
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