"""П'ять звичайних задач агентом ЛР4 (старий пошук search_service) - база для табл. 7.
У logs/lab4.log з ЛР4 є лише одна задача (запуск agent.py), тому прогін повторено тут
з тим самим кодом агента, моделлю й вікном 4096, але зі старим набором інструментів.
Запуск: python baseline_lab4.py   (лог: logs/run_lab4_tasks.log)"""
import json

import config

config.ALLOWED = ["search_service", "price_info", "calc_total"]   # набір інструментів ЛР4 - до імпорту schemas

from langfuse import get_client, propagate_attributes  # noqa: E402

import agent  # noqa: E402

with open("tasks.json", encoding="utf-8") as f:
    tasks = json.load(f)

for task in tasks:
    with propagate_attributes(trace_name=f"lab4-tasks-{task['id']}", tags=["lab4-tasks"]):
        agent.run_agent(task["question"], logfile_name="run_lab4_tasks", task_id=f"lab4-{task['id']}")

get_client().flush()
print("Лог: logs/run_lab4_tasks.log")
