"""Додаткове завдання: structured output (запобігання помилкам на сервері)."""
from openai import OpenAI
from pydantic import ValidationError

import config
from arguments import ARGS

TOOL = "calc_installment"
client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
schema = ARGS[TOOL].model_json_schema()

questions = [
    "Ноутбук коштує 27000 грн. Розстрочка на 6 місяців з переплатою 10%. Сформуй аргументи для розрахунку.",
    "Сформуй аргументи для розрахунку розстрочки: ціна 48000, 12 місяців, переплата 5%.",
    "Ціна 17500 грн, розстрочка на 3 місяці без переплати. Дай аргументи.",
    "Ціна 27000 грн, розстрочка на 0 місяців з переплатою 10%. Сформуй аргументи.",
    "Сформуй аргументи для розрахунку: мінус 27000 грн, 6 місяців, переплата 10%.",
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
