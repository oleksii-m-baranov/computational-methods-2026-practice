import json
from openai import OpenAI

import config
from arguments import ARGS

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
schema = ARGS["calc_calories"].model_json_schema()

response = client.chat.completions.create(
    model=config.MODEL,
    messages=[{"role": "user",
               "content": "Скільки калорій я спалю за 45 хвилин тренування при вазі 70 кг? Сформуй аргументи для розрахунку калорій."}],
               # "content": "Я займався інтенсивним бігом 60 хвилин, моя вага 85 кг, коефіцієнт навантаження 8. Сформуй аргументи."}],
               # "content": "Швидка ранкова розминка на 15 хвилин, вага людини 62 кг. Сформуй параметри."}],
               # "content": "Скільки калорій згорить за 0 хвилин при вазі 300 кг? Підготуй аргументи."}],
    response_format={"type": "json_schema",
                     "json_schema": {"name": "args", "schema": schema}},
)
text = response.choices[0].message.content

print(text)
print(ARGS["calc_calories"].model_validate_json(text))
