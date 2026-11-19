import json
from openai import OpenAI

import config
from arguments import ARGS

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
schema = ARGS["calc_calories"].model_json_schema()

response = client.chat.completions.create(
    model=config.MODEL,
    messages=[{"role": "user",
               #"content": "Скільки калорій я спалю за 45 хвилин при вазі 70 кг і коефіцієнті навантаження 5? Сформуй аргументи для обчислення калорій."}],
               # "content": "Тренування тривало дві години, вага сімдесят п'ять кілограмів, met вісім. Сформуй аргументи для обчислення калорій."}],
                #"content": "Я бігав 10 годин поспіль (600 хвилин), вага 70 кг, met 10. Сформуй аргументи для обчислення калорій."}],
               # "content": "Тренування 30 хвилин, вага 70 кг, коефіцієнт навантаження 50. Сформуй аргументи для обчислення калорій."}],
               #  "content": "Тренування 45 хвилин, вага 70 кг. Сформуй аргументи для обчислення калорій."}],
               "content": "Скільки буде сто доларів у гривнях? Курс 45. Сформуй аргументи для обчислення калорій."}],
    response_format={"type": "json_schema",
                     "json_schema": {"name": "args", "schema": schema}},
)
text = response.choices[0].message.content

print(text)
print(ARGS["calc_calories"].model_validate_json(text))