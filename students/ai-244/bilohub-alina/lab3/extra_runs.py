"""Додаткові питання, що провокують помилки моделі (для розбору трас у Langfuse).

Запускати з каталогу lab3 після основного прогону. Лог пишеться в окремий
файл logs/lab3_extra.log, щоб не змішувати його з lab3_checks.log.
"""
import config

config.LAB_LOGFILE_NAME = "lab3_extra"   # окремий лог (до імпорту agent)
config.RUN_TAG = "checks-extra"

from langfuse import get_client, propagate_attributes

from agent import run_agent

QUESTIONS = {
    "E1": "Скільки примірників книжки 'Мережі' є в наявності?",
    "E2": "Скільки буде 5 мінус 12? Порахуй інструментом.",
    "E3": "Поділи 20 на 4 за допомогою інструмента.",
    "E4": "Яка термін видачі книжки Місячний садівник?",
}

for qid, question in QUESTIONS.items():
    with propagate_attributes(trace_name=f"{config.RUN_TAG}-{qid}",
                              tags=[config.RUN_TAG]):
        run_agent(question)

get_client().flush()
