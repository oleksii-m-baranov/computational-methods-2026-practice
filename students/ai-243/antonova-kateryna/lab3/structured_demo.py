"""Перевірка підтримки Structured Output."""
import json
from openai import OpenAI

import config
from arguments import ARGS

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
schema = ARGS["calculate"].model_json_schema()

response = client.chat.completions.create(
    model=config.MODEL,
    messages=[{"role": "user",
               "content": "Скільки буде 15 плюс 27? Сформуй аргументи для обчислення."}],
    # Інші формулювання для повторних запусків, по одному на запуск:
    # "Скільки буде 8 помножити на 6? Сформуй аргументи для обчислення."
    # "Скільки буде 100 поділити на 4? Сформуй аргументи для обчислення."   # ділення немає в Literal
    # "Скільки буде 2 в десятому степені? Сформуй аргументи для обчислення." # степеня немає в Literal
    response_format={"type": "json_schema",
                     "json_schema": {"name": "args", "schema": schema}},
)
text = response.choices[0].message.content
print(text)
print(ARGS["calculate"].model_validate_json(text))