"""Демонстрація structured output: сервер сам не дає моделі порушити схему."""
import config
from arguments import ARGS
from langfuse.openai import OpenAI

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
schema = ARGS["calc_price"].model_json_schema()

questions = [
    "Порахуй 12 + 30. Сформуй аргументи для інструмента calc_price.",
    "Скільки буде 100 / 4? Сформуй аргументи для calc_price.",
    "Переведи 100 доларів у єни. Сформуй аргументи для calc_price.",
]

for question in questions:
    print(f"\n>>> {question}")
    try:
        r = client.chat.completions.create(
            model=config.MODEL,
            messages=[{"role": "user", "content": question}],
            response_format={
                "type": "json_schema",
                "json_schema": {"name": "args", "schema": schema},
            },
        )
        text = r.choices[0].message.content
        print(f"Сира відповідь: {text}")
        print(f"Перевірка Pydantic: {ARGS['calc_price'].model_validate_json(text)}")
    except Exception as e:
        print(f"ПОМИЛКА: {type(e).__name__}: {e}")