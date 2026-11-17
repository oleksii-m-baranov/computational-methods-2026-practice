"""Додаткове завдання: structured output. Сервер сам тримає відповідь у межах схеми."""
from openai import OpenAI
from pydantic import ValidationError

import config
from arguments import ARGS

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
schema = ARGS["calc_calories"].model_json_schema()

QUESTIONS = [
    "Скільки калорій я спалю за 45 хвилин тренування при вазі 70 кг і коефіцієнті 5? Сформуй аргументи для розрахунку калорій.",
    "Сформуй аргументи для розрахунку калорій: година бігу, я важу 80 кг, коефіцієнт навантаження 9.",
    "Сформуй аргументи для розрахунку калорій: 30 хвилин, вага 65 кг.",
    "Сформуй аргументи для розрахунку калорій: 45 хвилин, вага 700 кг, коефіцієнт 5.",
    "Сформуй аргументи для розрахунку калорій: 45 хвилин, вага 70 кг, коефіцієнт 100.",
]

for q in QUESTIONS:
    response = client.chat.completions.create(
        model=config.MODEL,
        messages=[{"role": "user", "content": q}],
        temperature=0,
        response_format={"type": "json_schema",
                         "json_schema": {"name": "args", "schema": schema}},
    )
    text = response.choices[0].message.content
    print("\nПИТАННЯ:", q)
    print("ВІДПОВІДЬ:", text)
    try:
        print("Pydantic: ок ->", ARGS["calc_calories"].model_validate_json(text))
    except ValidationError as error:
        print("Pydantic: ПОМИЛКА ->", error.errors()[0]["msg"])
