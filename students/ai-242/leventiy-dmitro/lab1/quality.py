from providers import make_client
import json

TEXT = """Сучасний смартфон може мати екран розміром 6,5 дюйма.
У деяких моделях встановлюють акумулятор ємністю 5000 мА·год.
Потужні смартфони можуть мати 8 або навіть 12 ГБ оперативної пам’яті.
Камера сучасного телефону може мати роздільну здатність 50 Мп.
Деякі смартфони підтримують заряджання потужністю 120 Вт.
Завдяки сучасним технологіям телефон може працювати без заряджання більше 24 годин.
"""

TASKS = {
    "1_fact": "У якому році вийшов перший iPhone? Відповідай лише роком.",
    "2_format": "Дай інформацію про перший iPhone у форматі JSON з полями product, year, company. Без пояснень, без markdown, лише JSON.",
    "3_summary": "Стисни наступний текст до двох речень, збережи всі числа:\n\n" + TEXT,
    "4_code": "Напиши функцію average_grade(grades), яка рахує середню оцінку зі списку, відкинувши найнижчу оцінку. Лише код.",
    "5_logic": "Сервер обробляє 1200 запитів за хвилину, 15% з них дають помилку, з цих помилкових запитів 40% повторюються успішно. Скільки запитів втрачено за годину? Покажи хід розв'язання.",
    "6_language": "Чим оперативна пам'ять відрізняється від жорсткого диска? Поясни українською, два абзаци.",
}

results = {}
for provider in ["cloud"]:
    client, model = make_client(provider)
    results[model] = {}
    for task_id, prompt in TASKS.items():
        answers = []
        for attempt in range(2):
            r = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            answers.append(r.choices[0].message.content)
        results[model][task_id] = answers
        print(f"{model} / {task_id} — готово")

with open("quality.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)