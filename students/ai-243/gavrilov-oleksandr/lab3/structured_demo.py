"""Додаткове завдання: запобігання помилкам на боці сервера."""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

import json
from openai import OpenAI

import config
from arguments import ARGS

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
schema = ARGS["calc_calories"].model_json_schema()

response = client.chat.completions.create(
    model=config.MODEL,
    messages=[{
        "role": "user",
        "content": "Скільки калорій я спалю за 45 хвилин тренування при вазі 70 кг? "
                   "Сформуй аргументи для розрахунку калорій.",
    }],
    response_format={
        "type": "json_schema",
        "json_schema": {"name": "args", "schema": schema},
    },
)
text = response.choices[0].message.content
print(text)
print(ARGS["calc_calories"].model_validate_json(text))
