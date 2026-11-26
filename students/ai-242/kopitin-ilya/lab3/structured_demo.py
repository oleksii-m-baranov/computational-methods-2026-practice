"""Додаткове завдання: structured output (запобігання помилкам на сервері)."""
from openai import OpenAI
from pydantic import ValidationError

import config
from arguments import ARGS

TOOL = "calc_total"
client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
schema = ARGS[TOOL].model_json_schema()

questions = [
    "Робота коштує 400 грн, одна деталь 250 грн, деталей чотири. Сформуй аргументи для розрахунку загальної вартості.",
    "Сформуй аргументи для розрахунку: робота 600 грн, деталь 900 грн, одна деталь.",
    "Розрахуй вартість: робота 500 грн, деталі не потрібні (0 грн), кількість 1. Дай аргументи.",
    "Робота 400 грн, деталь 250 грн, а кількість деталей нуль. Сформуй аргументи для розрахунку.",
    "Сформуй аргументи для розрахунку: робота мінус 400 грн, деталь 250 грн, кількість 4.",
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
