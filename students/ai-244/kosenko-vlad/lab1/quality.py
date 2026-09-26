import json
from providers import make_client

TEXT = """Космічний телескоп Джеймса Вебба було запущено 25 грудня 2021 року з космодрому Куру в Європейській Гвіані. Головне дзеркало апарата має діаметр 6,5 метра і складається з 18 шестикутних сегментів, вкритих чистим золотом. Телескоп працює на відстані близько 1,5 мільйона кілометрів від Землі в районі другої точки Лагранжа. Його місія розрахована щонайменше на 10 років досліджень раннього Всесвіту та екзопланет."""

TASKS = {
    "1_fact": "Рік першого польоту людини в космос. Відповідай лише роком.",
    "2_format": "JSON: event, year, person для першого польоту людини в космос. Без пояснень, без markdown, лише JSON.",
    "3_summary": "Стисни наступний текст до двох речень, збережи всі числа:\n\n" + TEXT,
    "4_code": "Напиши функцію light_travel_time(distance_km), яка повертає час проходження світла в секундах. Лише код.",
    "5_logic": "Зонд рухається зі швидкістю 60000 км/год, відстань становить 480 млн км. Скільки повних діб триватиме подорож? Покажи хід розв'язання.",
    "6_language": "Чим зоря відрізняється від планети. Поясни українською, два абзаци."
}

# Тестуємо три моделі згідно з інструкцією
PROVIDERS_TO_TEST = [
    ("local", "llama3.2:3b"),
    ("local", "qwen3:4b"),
    ("cloud", None)  # хмарний клієнт візьме модель зі словника PROVIDERS
]

results = {}

for provider_name, model_override in PROVIDERS_TO_TEST:
    client, default_model = make_client(provider_name)
    model = model_override if model_override else default_model

    results[model] = {}
    print(f"\n=== Запуск моделі: {model} ===")

    for task_id, prompt in TASKS.items():
        answers = []
        for attempt in range(2):  # два незалежні прогони
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

print("\nВсі результати успішно збережено у quality.json")