"""Додаткове завдання: запобігання помилкам на сервері (structured output)."""
from openai import OpenAI

import config
from arguments import ARGS

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
schema = ARGS["calc_total"].model_json_schema()

QUESTIONS = [
    "Заміна масла коштує: робота 400 грн, деталь 250 грн. Потрібно чотири літри. Сформуй аргументи для розрахунку вартості.",
    "Робота 600 грн, колодки по 900 грн, потрібна одна пара. Сформуй аргументи для розрахунку вартості.",
    "Робота коштує 25 євро, деталь 10 євро, потрібно 2 штуки. Сформуй аргументи для розрахунку вартості.",
    "Сформуй аргументи для розрахунку вартості: робота мінус 400 грн, деталь 250 грн, три деталі.",   # провокує межу gt=0
]

for question in QUESTIONS:
    response = client.chat.completions.create(
        model=config.MODEL,
        messages=[{"role": "user", "content": question}],
        response_format={"type": "json_schema",
                         "json_schema": {"name": "args", "schema": schema}},
    )
    text = response.choices[0].message.content
    print("ПИТАННЯ:", question)
    print("ВІДПОВІДЬ:", text)
    try:
        print("Pydantic:", ARGS["calc_total"].model_validate_json(text))
    except Exception as e:
        print("Pydantic відхилив:", e)
    print()
