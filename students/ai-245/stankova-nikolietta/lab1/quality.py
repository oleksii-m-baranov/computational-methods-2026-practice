from providers import make_client
import json

TEXT = """
Грошова реформа в Україні була проведена у вересні 1996 року. Під час реформи купоно-карбованці були замінені на гривню у співвідношенні 100000 до 1. Станом на 2025 рік Національний банк України випускає банкноти номіналом від 10 до 1000 гривень. Облікова ставка НБУ у різні роки змінювалася від 6% до понад 25%. Банківські депозити можуть приносити дохід у вигляді відсотків. Фонд гарантування вкладів фізичних осіб забезпечує захист коштів вкладників.
"""

TASKS = {
    "1_fact": "Рік уведення гривні як національної валюти. Відповідай лише роком.",

    "2_format": "JSON: currency, code, year. Без пояснень, без markdown, лише JSON.",

    "3_summary": "Стисни наступний текст до двох речень, збережи всі числа:\n\n" + TEXT,

    "4_code": "Напиши функцію compound_interest(principal, rate, years). Лише код.",

    "5_logic": "Депозит 20000 грн під 12% річних, податок 19,5% з відсотків. Скільки на руках через рік? Покажи хід розв'язання.",

    "6_language": "Чим акція відрізняється від облігації? Поясни українською, два абзаци.",
}

results = {}

for provider in ["llama", "qwen", "cloud"]:

    client, model = make_client(provider)

    results[model] = {}

    for task_id, prompt in TASKS.items():

        answers = []

        for attempt in range(2):

            try:
                r = client.chat.completions.create(
                    model=model,
                     messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                )

                answers.append(
                    r.choices[0].message.content
                )

            except Exception as e:
                answers.append(f"ERROR: {e}")
                print(f"Помилка: {model} / {task_id} / запуск {attempt + 1}")

        results[model][task_id] = answers

        print(f"{model} / {task_id} — готово")

with open(
    "quality.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        results,
        f,
        ensure_ascii=False,
        indent=2
    )

print("quality.json створено")