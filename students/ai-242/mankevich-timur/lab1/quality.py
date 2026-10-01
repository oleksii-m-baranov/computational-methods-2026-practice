import json
import os
from providers import make_client

# Текст для завдання 3 (тема варіанта 2 — транспорт). Факти: Вікіпедія,
# стаття «Київський метрополітен» (uk.wikipedia.org); вкажи це джерело у звіті.
TEXT = """Київський метрополітен відкрито 6 листопада 1960 року. Перша черга Святошино-Броварської лінії мала довжину 5,2 км і п'ять станцій — від «Вокзальної» до «Дніпра». Другу ділянку відкрили 1963 року. Нині в столиці діють три лінії, експлуатаційна довжина яких становить 69,648 км. Мережа налічує 52 станції, а в центрі міста розташовано три підземні вузли пересадки. Щодня метро працює з 05:30 до 23:00, а під час повітряної тривоги діє цілодобово як укриття."""

# Варіант 2
TASKS = {
    "1_fact": "Рік відкриття Київського метрополітену. Відповідай лише роком.",
    "2_format": "JSON: city, year, lines_count для Київського метро. "
                "Без пояснень, без markdown, лише JSON.",
    "3_summary": "Стисни наступний текст до двох речень, збережи всі числа:\n\n" + TEXT,
    "4_code": "Напиши Python-функцію total_weight(items), яка повертає суму ваг "
              "зі списку словників (вага лежить у ключі 'weight'). Лише код.",
    "5_logic": "120 ящиків: 45 по 8 кг, решта по 12 кг. Вантажівка тримає 1200 кг. "
               "Скільки рейсів? Покажи хід розв'язання.",
    "6_language": "Чим контейнерне перевезення відрізняється від навалочного. "
                  "Поясни українською, два абзаци.",
}

# (провайдер, модель); None = модель за замовчуванням із providers.py
RUNS = [
    ("local", "llama3.2:3b"),
    ("local", "qwen3:4b"),
    ("cloud", None),
]

OUT = "quality.json"

# Підхоплюємо вже наявні результати, щоб файл завжди лишався валідним JSON
# і кілька запусків не склеювались у кілька об'єктів підряд.
results = {}
if os.path.exists(OUT):
    with open(OUT, encoding="utf-8") as f:
        results = json.load(f)

for provider, model_override in RUNS:
    client, model = make_client(provider, model_override)
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
        print(f"{model} / {task_id} — готово")

    with open(OUT, "w", encoding="utf-8") as f:  # зберігаємо після кожної моделі
        json.dump(results, f, ensure_ascii=False, indent=2)
