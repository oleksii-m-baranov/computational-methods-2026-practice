from providers import make_client
import json

TEXT = """Ки́ївський метрополіте́н — швидкісна позавулична, переважно підземна, транспортна система Києва. 
Діють три лінії, експлуатаційна довжина яких становить 69,648 км. 52 станції із трьома підземними вузлами пересадки в центрі міста. 
Усі лінії електрифіковані постійною напругою 825 В, на них працюють 5-вагонні електропоїзди довжиною приблизно 100 м. 
Метрополітен відкритий для пасажирів щоденно з 05:30 до 23:00. 
Після відкриття став 14-м метрополітеном в Європі і 3-м у СРСР після московського та ленінградського."""

TASKS = {
    "1_fact": "Рік відкриття Київського метрополітену. Відповідай лише роком.",
    "2_format": "JSON з полями city, year, lines_count для Київського метро. Без пояснень, без markdown, лише JSON.",
    "3_summary": "Стисни наступний текст до двох речень, збережи всі числа:\n\n" + TEXT,
    "4_code": "total_weight(items) — сума ваг зі списку словників. Лише код.",
    "5_logic": "120 ящиків: 45 по 8 кг, решта по 12 кг. Вантажівка тримає 1200 кг. Скільки рейсів? Покажи хід розв'язання.",
    "6_language": "Чим контейнерне перевезення відрізняється від навалочного? Поясни українською, два абзаци.",
}

results = {}

for provider in ["local", "local_qwen", "cloud"]:
    client, model = make_client(provider)
    results[model] = {}
    for task_id, prompt in TASKS.items():
        answers = []
        for attempt in range(2):    # два прогони на завдання
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

