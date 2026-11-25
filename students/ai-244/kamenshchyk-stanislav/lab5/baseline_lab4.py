"""П'ять звичайних задач агентом ЛР4 (старий пошук search_service) - база для табл. 7.
У logs/lab4.log з ЛР4 є лише одна задача (запуск agent.py), тому прогін повторено тут
з тим самим кодом агента, моделлю й вікном 4096, але зі старим набором інструментів і тими
самими текстами, що бачила модель у ЛР4 (опис price_info і підказка перевірки згадують search_service).
Запуск: python baseline_lab4.py   (лог: logs/run_lab4_tasks.log)"""
import json

import config

config.ALLOWED = ["search_service", "price_info", "calc_total"]   # набір інструментів ЛР4 - до імпорту schemas

from langfuse import get_client, propagate_attributes  # noqa: E402

import agent  # noqa: E402
import dispatcher  # noqa: E402
import schemas  # noqa: E402

# опис price_info - як у ЛР4
schemas.set_description("price_info", schemas.DESCRIPTIONS["price_info"].replace(
    "або вона є у фрагментах, які повернув інструмент search_docs", "або повернув інструмент search_service"))

# підказка перевірки змісту - як у ЛР4
_check_lab5 = dispatcher.check_meaning


def check_meaning_lab4(name, args):
    problem = _check_lab5(name, args)
    return problem.replace("search_docs", "search_service") if problem else problem


dispatcher.check_meaning = check_meaning_lab4

with open("tasks.json", encoding="utf-8") as f:
    tasks = json.load(f)

for task in tasks:
    with propagate_attributes(trace_name=f"lab4-tasks-{task['id']}", tags=["lab4-tasks"]):
        agent.run_agent(task["question"], logfile_name="run_lab4_tasks", task_id=f"lab4-{task['id']}",
                        log_overwrite=task is tasks[0])   # лог очищається на першій задачі

get_client().flush()
print("Лог: logs/run_lab4_tasks.log")
