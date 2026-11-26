"""База для таблиці 7: п'ять задач з tasks.json на агенті лабораторної № 4.

Агент лаб. 4 = той самий цикл, але зі старим пошуком search_laptops (підрядком)
замість search_docs. Модель та сама (qwen25-3b-4k, вікно 4096), скорочення вимкнено.
Лог: logs/run_lab4.log

Запуск: python run_lab4_baseline.py
"""
import config

# до імпорту schemas/agent: старий набір інструментів і окремий лог
config.ALLOWED = ["search_laptops", "laptop_info", "calc_installment"]
config.LAB_LOGFILE_NAME = "run_lab4"
config.RUN_TAG = "lab4-baseline"

import runpy  # noqa: E402

runpy.run_path("agent_runner.py", run_name="__main__")
