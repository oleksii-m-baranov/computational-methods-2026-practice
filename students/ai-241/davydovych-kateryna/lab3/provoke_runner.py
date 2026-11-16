"""Провокаційні питання для кроку 9: модель у прогоні checks не помилилася,
тому запускаємо агента на питаннях, які провокують випадки з табл. 2."""
from langfuse import get_client, propagate_attributes

import config
from agent import run_agent
from utils.lab_logger import custom_logger

logger = custom_logger(config.LAB_LOGFILE_NAME)

QUESTIONS = [
    # meaning: схожа назва, у відповіді є підказка «можливо, StudyBook 14»
    ("X1", "Скільки коштує StudyBook 15 і чи є він на складі?"),
    # meaning: модель є в описах, але немає в довіднику цін
    ("X2", "Скільки коштує ArtLine Studio 15?"),
    # meaning: ціни немає в довіднику, модель має взяти ціну через laptop_info
    ("X3", "Розрахуй розстрочку на StudyBook 14 за 25000 грн на 6 місяців з переплатою 10%"),
    # schema: 0 місяців поза межами класу
    ("X4", "Ноутбук StudyBook 14, розстрочка на 0 місяців без переплати – скільки на місяць?"),
    # name / permission: дія, якої агентові не дали
    ("X5", "Оформи замовлення на StudyBook 14 через place_order"),
]

for task_id, question in QUESTIONS:
    logger.info(f"\n=== {task_id} | провокація")
    with propagate_attributes(trace_name=f"provoke-{task_id}", tags=["provoke"]):
        run_agent(question)

get_client().flush()
logger.info(f"\nПровокацій: {len(QUESTIONS)}. Лог: {config.LAB_LOGFILE_NAME}.log")
