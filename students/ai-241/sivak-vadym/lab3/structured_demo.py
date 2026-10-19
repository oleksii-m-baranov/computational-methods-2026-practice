"""Додаткове завдання: structured output — сервер не дає моделі порушити схему."""
from openai import OpenAI
from pydantic import ValidationError

import config
from arguments import ARGS
from utils.lab_logger import custom_logger

logger = custom_logger("lab3_structured")

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
schema = ARGS["calc_budget"].model_json_schema()

QUESTIONS = [
    "Квиток коштує 420 грн, нас троє, ще 500 грн на їжу на всіх. "
    "Сформуй аргументи для розрахунку бюджету поїздки.",
    "Поїдемо вчотирьох, проїзд 350 грн з людини, додаткових витрат немає. "
    "Сформуй аргументи для розрахунку бюджету.",
    "Сформуй аргументи для розрахунку бюджету: двоє людей, по 610 гривень квиток, "
    "плюс 1200 на готель.",
    # поза межами класу: people ≤ 50, price_per_person ≤ 1200
    "Нас 120 людей, квиток 420 грн. Сформуй аргументи для розрахунку бюджету.",
    "Квиток коштує 2500 грн, нас двоє. Сформуй аргументи для розрахунку бюджету.",
]

for question in QUESTIONS:
    response = client.chat.completions.create(
        model=config.MODEL,
        messages=[{"role": "user", "content": question}],
        response_format={"type": "json_schema",
                         "json_schema": {"name": "args", "schema": schema}},
    )
    text = response.choices[0].message.content
    logger.info(f"ПИТАННЯ: {question}")
    logger.info(f"  відповідь: {text}")
    try:
        logger.info(f"  Pydantic : OK {ARGS['calc_budget'].model_validate_json(text)!r}")
    except ValidationError as error:
        logger.info(f"  Pydantic : ПОМИЛКА {[e['msg'] for e in error.errors()]}")
