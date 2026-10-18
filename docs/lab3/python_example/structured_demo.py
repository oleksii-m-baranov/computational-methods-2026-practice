import json
from openai import OpenAI

import config
from arguments import ARGS

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
schema = ARGS["calculate"].model_json_schema()

response = client.chat.completions.create(
    model=config.MODEL,
    messages=[{"role": "user",
               "content": "Скільки буде сто доларів у гривнях? Курс долара в гривнях 45.0. Сформуй аргументи для переведення валюти."}],
               # "content": "Якщо площа прямокутника 150, а одна з його сторін дорівнює 10, то яка довжина іншої сторони? Сформуй аргументи для обчислення."}],
               # "content": "Скільки буде розділити 5 на 0? Сформуй аргументи для обчислення."}],
    response_format={"type": "json_schema",
                     "json_schema": {"name": "args", "schema": schema}},
)
text = response.choices[0].message.content

print(text)
print(ARGS["calculate"].model_validate_json(text))
