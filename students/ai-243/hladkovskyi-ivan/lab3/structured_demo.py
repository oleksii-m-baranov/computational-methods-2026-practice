"""Додаткове завдання: structured output (запобігання помилкам на сервері)."""
import sys
from openai import OpenAI

import config
from arguments import ARGS

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
schema = ARGS["calc_budget"].model_json_schema()

QUESTIONS = [
    "Поїздка втрьох, квиток 420 грн, ще 500 грн на їжу. Сформуй аргументи для розрахунку бюджету.",
    "Нас п'ятеро, проїзд по 300 грн, додаткових витрат немає. Сформуй аргументи для розрахунку бюджету.",
    # провокація: значення поза межами схеми
    "Група з нуля людей, квиток 420 грн. Сформуй аргументи для розрахунку бюджету.",
    "Нас двоє, квиток коштує мінус 100 грн. Сформуй аргументи для розрахунку бюджету.",
]
question = sys.argv[1] if len(sys.argv) > 1 else None

for q in ([question] if question else QUESTIONS):
    response = client.chat.completions.create(
        model=config.MODEL,
        messages=[{"role": "user", "content": q}],
        response_format={"type": "json_schema",
                         "json_schema": {"name": "args", "schema": schema}},
    )
    text = response.choices[0].message.content
    print("ПИТАННЯ:", q)
    print("ВІДПОВІДЬ:", text)
    try:
        print("Pydantic: OK ->", ARGS["calc_budget"].model_validate_json(text))
    except Exception as e:
        print("Pydantic: ПОМИЛКА ->", e)
    print()
