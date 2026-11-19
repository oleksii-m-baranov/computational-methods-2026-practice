"""Додаткове завдання: structured output (запобігання помилкам на сервері)."""
import config
from openai import OpenAI

from arguments import ARGS

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
schema = ARGS["calculate"].model_json_schema()

QUESTIONS = [
    "Скільки буде 5 помножити на 12? Сформуй аргументи для калькулятора.",
    "Додай 300 і 45. Сформуй аргументи для калькулятора.",
    "Відніми 7 від 20. Сформуй аргументи для калькулятора.",
    # операції ділення немає в Literal["mul", "add", "sub"]
    "Скільки буде 20 поділити на 4? Сформуй аргументи для калькулятора.",
]

for question in QUESTIONS:
    response = client.chat.completions.create(
        model=config.MODEL,
        messages=[{"role": "user", "content": question}],
        response_format={"type": "json_schema",
                         "json_schema": {"name": "args", "schema": schema}},
    )
    text = response.choices[0].message.content
    print(f"\nПитання : {question}")
    print(f"Відповідь: {text}")
    try:
        print("Pydantic : OK ->", ARGS["calculate"].model_validate_json(text))
    except Exception as error:
        print("Pydantic : НЕ ПРОЙШЛО ->", error)
