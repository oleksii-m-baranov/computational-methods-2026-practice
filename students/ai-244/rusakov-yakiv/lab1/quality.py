"""Завдання 5. Оцінювання якості моделей за рубрикою (варіант 8, тема «Туризм»).

Набір завдань зафіксовано до перегляду відповідей. Кожне завдання проганяється двічі.
Запуск для всіх трьох моделей: llama3.2:3b, qwen3:4b, хмарна.
"""
from logsetup import print  # друк іде і в консоль, і в lab1.log
import json
import os
import sys

from providers import make_client

# Текст для завдання 3: Одеський оперний театр.
# Джерело: https://uk.wikipedia.org/wiki/Одеський_національний_академічний_театр_опери_та_балету
TEXT = """Перша будівля Одеського театру опери та балету була відкрита 10 лютого 1810 року, \
і вона вміщувала близько 800 глядачів. У ніч на 2 січня 1873 року театр повністю знищила пожежа. \
Проєкт нової будівлі створили віденські архітектори Фердинанд Фельнер і Герман Гельмер, \
а перший камінь заклали 28 вересня 1884 року. Нинішня будівля була урочисто відкрита 13 жовтня 1887 року. \
Повну реставрацію споруди завершили у 2007 році. \
Того самого року театр отримав статус національного."""

TASKS = {
    "1_fact":     "Рік відкриття нинішньої будівлі Одеського оперного театру. Відповідай лише роком.",
    "2_format":   "Дай JSON з полями landmark, city, year для нинішньої будівлі Одеського оперного театру. "
                  "Без пояснень, без markdown, лише JSON.",
    "3_summary":  "Стисни наступний текст до двох речень, збережи всі числа:\n\n" + TEXT,
    "4_code":     "Напиши функцію Python trip_cost(days, daily_cost, transport), яка повертає загальну "
                  "вартість поїздки: кількість днів, помножена на вартість доби, плюс вартість дороги. Лише код.",
    "5_logic":    "Поїздка 6 днів: житло 900/добу, їжа 500/день, дорога 2400. Троє, житло й дорога порівну. "
                  "Скільки заплатить кожен? Покажи хід розв'язання.",
    "6_language": "Чим хостел відрізняється від готелю. Поясни українською, два абзаци.",
}

# Можна запускати частинами: `python quality.py cloud` — результати додаються до quality.json
providers = sys.argv[1:] or ["local", "local_qwen", "cloud"]
results = {}
if os.path.exists("quality.json"):
    with open("quality.json", encoding="utf-8") as f:
        results = json.load(f)

for provider in providers:
    client, model = make_client(provider)
    results[model] = {}
    for task_id, prompt in TASKS.items():
        answers = []
        for attempt in range(2):          # два прогони на завдання
            r = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            answers.append(r.choices[0].message.content)
        results[model][task_id] = answers
        print(f"{model} / {task_id} — готово")
    with open("quality.json", "w", encoding="utf-8") as f:   # зберігаємо після кожної моделі
        json.dump(results, f, ensure_ascii=False, indent=2)
