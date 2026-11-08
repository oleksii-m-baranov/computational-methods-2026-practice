"""Завдання 5. Оцінювання якості моделей за рубрикою (варіант 7, «Кіно»)."""
import json

from providers import make_client
from utils.lab_logger import custom_logger

logger = custom_logger('lab1')

# Джерело: https://uk.wikipedia.org/wiki/Одеська_кіностудія
TEXT = """Одеська кіностудія веде свою історію з 1907 року. \
У 1919 році на базі приватних кінофабрик Борисова та Харитонова утворена Одеська кінофабрика. \
У радянський час на Одеській кіностудії зняли понад 350 кінофільмів. \
Вона є однією з найдавніших у світі та може похвалитися понад 700 фільмами різних жанрів. \
Станом на 2015 рік 50 %+1 акцій ПрАТ «Одеська кіностудія» знаходяться в державній власності. \
Наприкінці травня 2019 року на Одеській кіностудії відзначили 100-річний ювілей від часу заснування."""

TASKS = {
    "1_fact": "Рік першого публічного кінопоказу братів Люм'єр. Відповідай лише роком.",
    "2_format": "Рік першого публічного кінопоказу братів Люм'єр. JSON: event, year, city. "
                "Без пояснень, без markdown, лише JSON.",
    "3_summary": "Стисни наступний текст до двох речень, збережи всі числа:\n\n" + TEXT,
    "4_code": "Напиши функцію top_rated(films, n) — n найкращих фільмів за рейтингом. Лише код.",
    "5_logic": "Зал 180 місць, сеанс 1 год 45 хв + 15 хв перерва, робота з 10:00 до 23:00. "
               "Скільки сеансів і глядачів? Покажи хід розв'язання.",
    "6_language": "Чим документальне кіно відрізняється від художнього. Поясни українською, два абзаци.",
}

results = {}

for provider in ["local", "local_qwen", "cloud"]:
    client, model = make_client(provider)
    results[model] = {}

    for task_id, prompt in TASKS.items():
        answers = []

        for attempt in range(2):  # два прогони на завдання
            r = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            answers.append(r.choices[0].message.content)
        results[model][task_id] = answers
        logger.info(f"{model} / {task_id} — готово")
        for i, a in enumerate(answers, 1):
            logger.info(f"  прогін {i}:\n{a}")

with open("quality.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
logger.info("Відповіді збережено в quality.json")
