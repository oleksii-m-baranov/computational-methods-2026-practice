"""Додатковий прогін: питання, що провокують помилки перевірок (розд. 7.3 звіту).
Запуск з папки lab3:  python extra_run.py        (усі питання)
                      python extra_run.py E1 E3   (тільки вибрані)
Трасу в Langfuse буде названо checks-E1, checks-E2 тощо (мітка checks). Лог — новий lab3.log."""
import sys

from langfuse import get_client, propagate_attributes

import config
from agent import run_agent
from utils.lab_logger import custom_logger

logger = custom_logger(config.LAB_LOGFILE_NAME)

QUESTIONS = {
    "E1": "Скільки коштує ноутбук ColorLab 15?",                                   # очікую meaning
    "E2": "Порадь ноутбук для дизайну і скажи, скільки він коштує",               # search поверне PixelStudio 16 і ColorLab 15
    "E3": "Ноутбук LearnPad 14 коштує 27000 грн. Порахуй розстрочку на 0 місяців з переплатою 10%",  # очікую schema (months)
    "E4": "Порахуй розстрочку на 6 місяців з переплатою 10% для ноутбука за мінус 27000 грн",         # очікую schema (price)
}

ids = sys.argv[1:] or list(QUESTIONS)
for qid in ids:
    logger.info(f"\n### {qid} | додатковий прогін")
    with propagate_attributes(trace_name=f"{config.RUN_TAG}-{qid}", tags=[config.RUN_TAG]):
        run_agent(QUESTIONS[qid])

get_client().flush()
logger.info(f"\nГотово. Лог: {config.LAB_LOGFILE_NAME}.log")
