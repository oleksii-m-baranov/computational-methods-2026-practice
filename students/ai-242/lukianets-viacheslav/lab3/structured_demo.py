"""Додаткове завдання: запобігання помилкам через structured output."""
from openai import OpenAI

import config
from arguments import ARGS

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
schema = ARGS["calculate"].model_json_schema()

QUESTIONS = [
    "Я затримав книжку на 5 днів, штраф 10 грн/день. Скільки треба заплатити? "
    "Сформуй аргументи для обчислення.",
    "Візьми 12 і додай до нього 30. Сформуй аргументи для обчислення.",
    # провокація: ділення — значення, якого немає в Literal["mul","add","sub"]
    "Скільки буде 100 поділити на 4? Сформуй аргументи для обчислення.",
]

for question in QUESTIONS:
    response = client.chat.completions.create(
        model=config.MODEL,
        messages=[{"role": "user", "content": question}],
        response_format={"type": "json_schema",
                         "json_schema": {"name": "args", "schema": schema}},
    )
    text = response.choices[0].message.content
    print("ЗАПИТ:", question)
    print("СИРИЙ JSON:", text)
    try:
        print("Pydantic:", ARGS["calculate"].model_validate_json(text))
    except Exception as e:
        print("Pydantic ПОМИЛКА:", e)
    print()
