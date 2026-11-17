"""Завдання 5. Оцінювання якості моделей за рубрикою (варіант 4, тема «Спорт»)."""
import json
from providers import make_client, sampling_params, get_logger

log = get_logger()

# Джерело: https://olympics.com/en/olympic-games/athens-1896
TEXT = """Перші сучасні Олімпійські ігри відбулися в Афінах з 6 по 15 квітня 1896 року.
У змаганнях взяв участь 241 спортсмен із 14 країн, і всі вони були чоловіками.
Атлети розіграли 43 комплекти нагород у 9 видах спорту.
Головною ареною став відреставрований Панатінаїкос, а на церемонії відкриття були присутні близько 60 тисяч глядачів.
Найбільше медалей, 47, здобула країна-господарка Греція.
Переможцям вручали срібні медалі й оливкові гілки, а не золоті медалі."""

TASKS = {
    "1_fact":     "Рік перших сучасних Олімпійських ігор. Відповідай лише роком.",
    "2_format":   "JSON: event, year, city для перших сучасних Олімпійських ігор. "
                  "Без пояснень, без markdown, лише JSON.",
    "3_summary":  "Стисни наступний текст до двох речень, збережи всі числа:\n\n" + TEXT,
    "4_code":     "Напиши функцію Python win_rate(results), яка приймає список результатів "
                  "матчів 'W'/'L'/'D' і повертає частку перемог. Лише код.",
    "5_logic":    "8 команд, кожна грає з кожною по разу. Скільки матчів? "
                  "При 4 матчах на день — скільки днів? Покажи хід розв'язання.",
    "6_language": "Чим спринт відрізняється від стаєрського бігу. Поясни українською, два абзаци.",
}

results = {}

for provider in ["local", "local_qwen", "cloud"]:
    client, model = make_client(provider)
    results[model] = {}
    for task_id, prompt in TASKS.items():
        answers = []
        for attempt in range(2):          # два прогони на завдання
            r = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                **sampling_params(provider, temperature=0.7),
            )
            answers.append(r.choices[0].message.content)
        results[model][task_id] = answers
        print(f"{model} / {task_id} — готово")
        log.info(f"[quality] {model} / {task_id}: {answers!r}")

with open("quality.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
