"""Додаткове завдання: запобігання помилкам на сервері через structured output."""
from openai import OpenAI

import config
from arguments import ARGS
from utils.lab_logger import custom_logger

logger = custom_logger("lab3_structured", overwrite=True)
client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
schema = ARGS["calc_materials"].model_json_schema()

prompts = [
    (
        "Кейс 1 (валідні дані, фарбування стін)",
        "Скільки інтер'єрної фарби потрібно на стіни площею 24 м², якщо одна банка покриває 17 м² і коштує 890 грн? "
        "Сформуй аргументи для розрахунку матеріалів.",
    ),
    (
        "Кейс 2 (інше формулювання, укладання плитки)",
        "Коридор має площу 11 квадратних метрів. Упаковка керамічної плитки коштує 970 гривень і розрахована на 1.8 квадратних метра. "
        "Сформуй JSON-аргументи для обчислення потрібної кількості та вартості.",
    ),
    (
        "Кейс 3 (провокація: нульове покриття з довідника — ізоляційна стрічка)",
        "Порахуй матеріали для електромонтажу на 21 м², якщо ізоляційна стрічка коштує 145 грн, а її покриття 0 м². "
        "Сформуй аргументи для розрахунку.",
    ),
    (
        "Кейс 4 (провокація: від'ємна площа та поза межами схеми)",
        "Сформуй аргументи розрахунку для площі -15 м², покриття 6.4 м² і ціни 385 грн.",
    ),
]

for label, prompt in prompts:
    logger.info(f"\n=== {label} ===")
    logger.info(f"Запит: {prompt}")
    try:
        response = client.chat.completions.create(
            model=config.MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=config.TEMPERATURE,
            response_format={
                "type": "json_schema",
                "json_schema": {"name": "calc_materials_args", "schema": schema},
            },
        )
        text = response.choices[0].message.content
        logger.info(f"Відповідь моделі (JSON): {text}")
        parsed = ARGS["calc_materials"].model_validate_json(text)
        logger.info(f"Pydantic OK: {parsed}")
    except Exception as error:
        logger.error(f"Помилка перевірки або виклику: {type(error).__name__}: {error}")
