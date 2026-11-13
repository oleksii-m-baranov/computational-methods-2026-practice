import json
from openai import OpenAI
import config
from arguments import ARGS

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)

schema = ARGS["convert_currency"].model_json_schema()

test_queries = [
    # Звичайні коректні формулювання
    "Скільки буде сто доларів у гривнях?",
    "Переведи 500 EUR в UAH.",
    "Хочу обміняти 250 гривень на долари США, підготуй аргументи.",
    "Конвертуй 1250.50 доларів у євро.",

    # Питання зі значенням ПОЗА переліком Literal
    "Скільки буде 1000 японських єн (JPY) у гривнях (UAH)?",
    "Переведи 500 польських злотих (PLN) у євро (EUR)."
]

for query in test_queries:
    response = client.chat.completions.create(
        model=config.MODEL,
        messages=[
            {
                "role": "user",
                "content": f"{query} Сформуй аргументи для переведення валюти."
            }
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "convert_currency_args",
                "strict": True,
                "schema": schema
            }
        },
    )

    print("---------------------------------------")
    text = response.choices[0].message.content
    print("Згенерований JSON моделі:")
    print(text)

    validated_args = ARGS["convert_currency"].model_validate_json(text)
    print("\nУспішно провалідовано Pydantic:")
    print(validated_args)
    print("---------------------------------------")
    print()