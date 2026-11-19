"""Додаткове завдання: structured output (запобігання помилкам на сервері)."""
from openai import OpenAI
from pydantic import ValidationError

import config
from arguments import ARGS

TOOL = "calc_price"
client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
schema = ARGS[TOOL].model_json_schema()

questions = [
    "Посилка важить 15 кг, ціна 18 грн за кілограм, мінімальна вартість 70 грн. Сформуй аргументи для розрахунку.",
    "Сформуй аргументи для розрахунку: 2 кг, 20 грн за кілограм, мінімум 75 грн.",
    "Сформуй аргументи для розрахунку: 8,5 кг, тариф 14 грн/кг, мінімальна вартість 60 грн.",
    "Посилка важить 50 кг, 18 грн за кілограм, мінімум 70 грн. Сформуй аргументи для розрахунку.",
    "Сформуй аргументи для розрахунку: мінус 5 кг, 18 грн за кілограм, мінімум 70 грн.",
]

for q in questions:
    print("ПИТАННЯ:", q)
    response = client.chat.completions.create(
        model=config.MODEL,
        messages=[{"role": "user", "content": q}],
        response_format={"type": "json_schema",
                         "json_schema": {"name": "args", "schema": schema}},
    )
    text = response.choices[0].message.content
    print("ВІДПОВІДЬ:", text)
    try:
        print("Pydantic: OK ->", ARGS[TOOL].model_validate_json(text), "\n")
    except ValidationError as error:
        print("Pydantic: НЕ ПРОЙШЛО ->", error.errors()[0]["msg"], "\n")
