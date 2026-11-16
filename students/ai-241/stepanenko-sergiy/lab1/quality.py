from providers import make_client
import json

TEXT = """Марс — четверта планета Сонячної системи, яку часто називають Червоною планетою через характерний колір її поверхні. Середній радіус Марса становить приблизно 3390 км, що майже вдвічі менше за радіус Землі. Середня відстань від Марса до Сонця становить 228 мільйонів кілометрів, або 1,5 астрономічної одиниці. Один оберт навколо своєї осі Марс здійснює приблизно за 24,6 години. Марсіанський рік триває 687 земних діб, оскільки планета рухається навколо Сонця довше, ніж Земля. Вісь обертання Марса нахилена приблизно на 25 градусів, завдяки чому на планеті спостерігаються зміни пір року"""

TASKS = {
    "1_fact": "Рік першого польоту людини в космос. Відповідай лише роком.",
    "2_format": "JSON: event, year, person. Без пояснень, без markdown, лише JSON.",
    "3_summary": "Стисни наступний текст до двох речень, збережи всі числа: \n\n" + TEXT,
    "4_code": "light_travel_time (distance_km). Лише код.",
    "5_logic": "Зонд 60000 км/год, відстань 480 млн км. Скільки повних діб? Покажи хід розв'язання.",
    "6_language": "Чим зоря відрізняється від планети. Поясни українською, два абзаци.",
}

results = {}

for provider in ["local", "qwen", "cloud"]:
    client, model = make_client(provider)
    results[model] = {}
    for task_id, prompt in TASKS.items():
        answers = []
        for attempt in range(2): # два прогони на завдання
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