import json
from providers import make_client

TEXT = """Одеський національний академічний театр опери та балету був відкритий 1 жовтня 1887 року за проєктом віденських архітекторів Фельнера і Гельмера. Глядацька зала театру виконана у стилі пізнього французького рококо та розрахована на 1636 місць. У 2007 році завершилася масштабна реставрація будівлі, яка тривала понад 11 років і зміцнила її фундамент на 1800 палях. Щороку театр відвідують понад 250 тисяч туристів та мешканців міста з різних країн світу."""

TASKS = {
    "1_fact": "Рік відкриття нинішньої будівлі Одеського оперного театру. Відповідай лише роком.",
    "2_format": "JSON: landmark, city, year для нинішньої будівлі Одеського оперного театру. Без пояснень, без markdown, лише JSON.",
    "3_summary": f"Стисни наступний текст до двох речень, збережи всі числа:\n\n{TEXT}",
    "4_code": "Напиши функцію trip_cost(days, daily_cost, transport), яка обчислює загальну вартість подорожі. Лише код.",
    "5_logic": "Поїздка 6 днів: житло 900/добу, їжа 500/день, дорога 2400. Троє, житло й дорога порівну. Скільки заплатить кожен? Покажи хід розв'язання.",
    "6_language": "Чим хостел відрізняється від готелю. Поясни українською, два абзаци."
}

PROVIDERS_TO_TEST = [
    ("local", "llama3.2:3b"),
    ("local", "qwen3:4b"),
    ("cloud", None)
]

results = {}

for provider_name, model_override in PROVIDERS_TO_TEST:
    client, default_model = make_client(provider_name)
    model = model_override if model_override else default_model

    results[model] = {}
    print()
    print(f"=== Запуск моделі: {model} ===")

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
        print(f"{model} / {task_id} готово")

with open("quality.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print()
print("Всі результати успішно збережено у quality.json")