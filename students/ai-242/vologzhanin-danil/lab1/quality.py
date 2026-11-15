from providers import make_client
import json


TEXT = """12 квітня 1961 року Юрій Гагарін здійснив перший в історії людства космічний політ на кораблі «Восток-1». Ракета-носій стартувала з космодрому Байконур о 09:07 за місцевим часом. Політ тривав усього 108 хвилин, за які космічний корабель здійснив 1 повний оберт навколо Землі. Максимальна висота орбіти становила 327 кілометрів, а мінімальна — 181 кілометр. Після виконання завдання космонавт катапультувався на висоті 7 кілометрів і успішно спустився на парашуті."""

TASKS = {
    "1_fact": "Рік першого польоту людини в космос. Відповідай лише роком.",
    "2_format": "Створи JSON: event, year, person для першого польоту людини в космос. Без пояснень, без markdown, лише JSON.",
    "3_summary": "Стисни наступний текст до двох речень, збережи всі числа:\n\n" + TEXT,
    "4_code": "Напиши функцію light_travel_time(distance_km). Лише код.",
    "5_logic": "Зонд летить зі швидкістю 60000 км/год, відстань 480 млн км. Скільки повних діб триватиме політ? Покажи хід розв'язання.",
    "6_language": "Чим зоря відрізняється від планети. Поясни українською, два абзаци.",
}

results = {}

for provider in ["local", "local2", "cloud"]:
    client, model = make_client(provider)
    print(f"Provider: {provider} | Model: {model}")
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

print("quality.json saved.")

