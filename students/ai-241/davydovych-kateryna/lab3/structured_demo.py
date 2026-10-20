"""Додаткове завдання: structured output – запобігання помилкам на сервері."""
import sys

from openai import OpenAI
from pydantic import ValidationError

import config
from arguments import ARGS

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
schema = ARGS["calc_installment"].model_json_schema()

QUESTIONS = [
    "Ноутбук коштує 24000 грн. Скільки платити на місяць при розстрочці "
    "на 6 місяців з переплатою 10%? Сформуй аргументи для розрахунку розстрочки.",
    "Хочу взяти ноутбук за двадцять чотири тисячі гривень на пів року, "
    "переплата десять відсотків. Сформуй аргументи для розрахунку розстрочки.",
    "Ціна 52000 грн, розстрочка на рік без переплати. "
    "Сформуй аргументи для розрахунку розстрочки.",
    # провокація: значення поза межами схеми (months <= 24)
    "Ноутбук за 24000 грн, розстрочка на 5 років з переплатою 30%. "
    "Сформуй аргументи для розрахунку розстрочки.",
]

if len(sys.argv) > 1:                    # можна передати своє питання
    QUESTIONS = [" ".join(sys.argv[1:])]

for question in QUESTIONS:
    response = client.chat.completions.create(
        model=config.MODEL,
        messages=[{"role": "user", "content": question}],
        temperature=config.TEMPERATURE,
        response_format={"type": "json_schema",
                         "json_schema": {"name": "args", "schema": schema}},
    )
    text = response.choices[0].message.content
    print(f"ПИТАННЯ : {question}")
    print(f"ВІДПОВІДЬ: {text}")
    try:
        print(f"PYDANTIC: OK -> {ARGS['calc_installment'].model_validate_json(text)}")
    except ValidationError as error:
        print(f"PYDANTIC: ПОМИЛКА -> {error.errors()}")
    print("-" * 60)
