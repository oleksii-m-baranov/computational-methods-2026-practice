from providers import make_client
import json

TEXT = """Київський метрополітен був урочисто відкритий 6 листопада 1960 року. На момент відкриття він складався з 5 станцій розташованих на одній лінії протяжністю 5.2 кілометра. Сьогодні підземка налічує 3 діючі лінії загальною довжиною понад 67 кілометрів. Мережа охоплює 52 станції, серед яких є найглибша станція у світі — Арсенальна. Щодня метрополітен перевозить близько 1.4 мільйона пасажирів."""

TASKS = {
    "1_fact": "Рік відкриття Київського метрополітену. Відповідай лише роком.",
    "2_format": "Згенеруй JSON з полями city, year, lines_count для Київського метро. Без пояснень, без markdown, лише JSON.",
    "3_summary": "Стисни наступний текст до двох речень, збережи всі числа:\n\n" + TEXT,
    "4_code": "Напиши функцію Python total_weight(items) для розрахунку суми ваг зі списку словників. Лише код.",
    "5_logic": "Є 120 ящиків: 45 по 8 кг, решта по 12 кг. Вантажівка тримає 1200 кг. Скільки рейсів потрібно? Покажи хід розв'язання.",
    "6_language": "Поясни чим контейнерне перевезення відрізняється від навалочного. Поясни українською, два абзаци.",
}

results = {}
for provider in ["local", "cloud"]:
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