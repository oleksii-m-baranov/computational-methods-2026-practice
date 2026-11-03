from providers import make_client
import json

TEXT = """Національний банк України було засновано в 1991 році після проголошення незалежності
країни. У 1996 році в обіг було введено національну валюту — гривню, замінивши
тимчасові купоно-карбованці. Станом на 2023 рік облікова ставка НБУ становила 15%.
Українська біржа облігацій внутрішньої державної позики (ОВДП) залучила у 2023 році
понад 400 мільярдів гривень. Мінімальний розмір статутного капіталу банку в Україні
встановлено на рівні 200 мільйонів гривень."""

TASKS = {
    "1_fact": "Рік уведення гривні як національної валюти. Відповідай лише роком.",
    "2_format": "Дай JSON з полями currency, code, year для гривні. Без пояснень, без markdown, лише JSON.",
    "3_summary": "Стисни наступний текст до двох речень, збережи всі числа:\n\n" + TEXT,
    "4_code": "Напиши функцію compound_interest(principal, rate, years), яка рахує складні відсотки (річна капіталізація). Лише код.",
    "5_logic": "Депозит 20000 грн під 12% річних, податок 19,5% з відсотків. Скільки коштів буде на руках через рік? Покажи хід розв'язання.",
    "6_language": "Чим акція відрізняється від облігації? Поясни українською, два абзаци.",
}

results = {}
for provider in ["local", "cloud", "local1"]:
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
        print(f"{model} / {task_id} — готово")

with open("quality.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("Готово: quality.json")