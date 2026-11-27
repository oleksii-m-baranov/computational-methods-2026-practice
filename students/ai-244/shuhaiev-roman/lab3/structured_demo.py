"""Додаткове завдання: structured output (запобігання помилкам на сервері)."""
import json
import os

from openai import OpenAI
from pydantic import ValidationError

import config
from arguments import ARGS

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
schema = ARGS["calc_calories"].model_json_schema()

QUESTIONS = [
    "Скільки калорій я спалю за 45 хвилин тренування при вазі 70 кг? Сформуй аргументи для розрахунку калорій.",
    "Я важу 82 кілограми і бігав пів години з MET 9. Сформуй аргументи для розрахунку калорій.",
    "Півтори години йоги, вага шістдесят кілограмів. Сформуй аргументи для розрахунку калорій.",
    # значення поза межами класу: вага 700 кг (допустимо 30..250)
    "Скільки калорій спалить слон вагою 700 кг за 45 хвилин? Сформуй аргументи для розрахунку калорій.",
]

results = []
for q in QUESTIONS:
    response = client.chat.completions.create(
        model=config.MODEL,
        messages=[{"role": "user", "content": q}],
        response_format={"type": "json_schema",
                         "json_schema": {"name": "args", "schema": schema}},
    )
    text = response.choices[0].message.content
    try:
        parsed = ARGS["calc_calories"].model_validate_json(text)
        verdict = f"OK: {parsed}"
    except ValidationError as e:
        verdict = "ValidationError: " + "; ".join(f"{err['loc']}: {err['msg']}" for err in e.errors())
    print(f"Питання: {q}\nВідповідь: {text}\nPydantic: {verdict}\n")
    results.append({"question": q, "answer": text, "pydantic": verdict})

os.makedirs("results", exist_ok=True)
with open("results/structured_demo.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
