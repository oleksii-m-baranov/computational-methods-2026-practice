from providers import make_client
import json
import os

TEXT = "Київський метрополітен є швидкісною транспортною системою столиці України. Його першу ділянку довжиною 5,2 км було відкрито у 1960 році у складі п'яти станцій. Станом на 2026 рік загальна протяжність ліній становить понад 70 кілометрів."

TASKS = {
    "1_fact": "Рік відкриття Київського метрополітену. Відповідай лише роком.",
    "2_format": "Поверни інформацію про Київське метро у форматі JSON із полями: city, year, lines_count. Без пояснень, без markdown, лише JSON.",
    "3_summary": "Стисни наступний текст до двох речень, збережи всі числа:\n\n" + TEXT,
    "4_code": "Напиши функцію total_weight(items), яка рахує суму ваг зі списку словників. Лише код.",
    "5_logic": "120 ящиків: 45 по 8 кг, решта по 12 кг. Вантажівка тримає 1200 кг. Скільки рейсів потрібно для перевезення? Покажи хід розв'язання.",
    "6_language": "Чим контейнерне перевезення відрізняється від навалочного? Поясни українською, два абзаци.",
}

results = {}
if os.path.exists("quality.json"):
    with open("quality.json", "r", encoding="utf-8") as f:
        try:
            results = json.load(f)
        except json.JSONDecodeError:
            pass

client, model_name = make_client("local")
results[model_name] = {}

print(f"Тестуємо модель: {model_name}")

for task_id, prompt in TASKS.items():
    print(f"Виконується завдання: {task_id}...")
    answers = []
    for attempt in range(2):
        try:
            r = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            answers.append(r.choices[0].message.content)
        except Exception as e:
            answers.append(f"Помилка: {str(e)}")
    results[model_name][task_id] = answers
    print(f" > {task_id} – готово!")

with open("quality.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("Усі результати успішно збережено у quality.json!")