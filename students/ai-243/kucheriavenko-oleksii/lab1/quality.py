import json
from providers import make_client

TEXT = """Національний банк України ввів у обіг національну валюту гривню під час грошової реформи з 2 по 16 вересня 1996 року. Обмін старих українських карбованців на гривні проводився за курсом 100 000 карбованців за 1 гривню. Протягом перших двох тижнів реформи в обіг було випущено понад 3,1 мільярда гривень готівкою. У 2019 році до обігу ввели монети номіналом 5 гривень, а у 2020 році — монети номіналом 10 гривень."""

TASKS = {
    "1_fact": "Рік уведення гривні як національної валюти. Відповідай лише роком.",
    "2_format": "Поверни JSON з полями currency, code, year для української гривні. Без пояснень, без markdown, лише JSON.",
    "3_summary": "Стисни наступний текст до двох речень, збережи всі числа:\n\n" + TEXT,
    "4_code": "Напиши функцію Python compound_interest(principal, rate, years) для розрахунку суми зі складними відсотками. Лише код.",
    "5_logic": "Депозит 20000 грн під 12% річних, податок 19,5% з відсотків. Скільки на руках через рік? Покажи хід розв'язання.",
    "6_language": "Чим акція відрізняється від облігації. Поясни українською, два абзаци.",
}

results = {}
for provider in ["local", "local_reason", "cloud"]:
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
print("Збережено quality.json")
