"""Завдання 5: оцінювання якості за рубрикою (варіант 1). Дві відповіді на кожне завдання."""
import json
from providers import make_client
from utils.lab_logger import custom_logger

logger = custom_logger("lab1")

# Джерело: uk.wikipedia.org, «Одеський національний університет імені І. І. Мечникова»
TEXT = """Одеський національний університет імені І. І. Мечникова заснований у 1865 році як Імператорський Новоросійський університет. Нині в ньому діє 12 факультетів. Загальний контингент студентів становить близько 14500 осіб. Загальна кількість співробітників університету становить приблизно 3500 осіб. Серед науково-педагогічних працівників є 179 докторів наук, професорів. Аспіранти навчаються за 105 спеціальностями."""

TASKS = {
    "1_fact": "Рік заснування Одеського національного університету імені І. І. Мечникова. Відповідай лише роком.",
    "2_format": "JSON: name, year, city для Одеського національного університету імені І. І. Мечникова. Без пояснень, без markdown, лише JSON.",
    "3_summary": "Стисни наступний текст до двох речень, збережи всі числа:\n\n" + TEXT,
    "4_code": "is_palindrome(s), ігнорує пробіли й регістр. Лише код.",
    "5_logic": "25 студентів, 12 знають Python, 9 Java, 4 обидві. Скільки не знають жодної? Покажи хід розв'язання.",
    "6_language": "Чим стек відрізняється від черги. Поясни українською, два абзаци.",
}

results = {}

for provider in ["local_llama", "local_qwen", "cloud"]:
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

with open("quality.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
