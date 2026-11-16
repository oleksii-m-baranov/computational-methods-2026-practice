"""Крок 9: питання, що провокують помилку моделі, для розбору трас у Langfuse.
Окрема мітка й окремий лог, щоб не змішувати з основним прогоном checks."""
import config

config.RUN_TAG = "demo"
config.LAB_LOGFILE_NAME = "lab3_demo"

from langfuse import get_client, propagate_attributes  # noqa: E402

from agent import run_agent  # noqa: E402

QUESTIONS = {
    "D1": "Скільки вийде поїздка вдвох до Яремче, плюс 400 грн на їжу?",
    "D2": "Скільки вийде поїздка втрьох до Коблева, якщо ще 900 грн на житло на всіх?",
}

for qid, question in QUESTIONS.items():
    with propagate_attributes(trace_name=f"{config.RUN_TAG}-{qid}", tags=[config.RUN_TAG]):
        run_agent(question)

get_client().flush()
