import json
from providers import make_client


TEXT = """Одеський національний університет імені І. І. Мечникова є одним із найстаріших закладів вищої освіти в Україні.
Історія цього славетного вишу розпочалася 13 травня 1865 року, коли його було створено на базі Рішельєвського ліцею.
Спочатку навчальний заклад функціонував під назвою Імператорський Новоросійський університет і мав три факультети.
Ім'я видатного біолога та Нобелівського лауреата Іллі Мечникова було присвоєно університету у 1945 році.
За півтора століття своєї діяльності заклад випустив понад чверть мільйона висококласних фахівців.
Сьогодні ОНУ залишається провідним науково-освітнім та культурним осередком південного регіону країни."""

TASKS = {
    "1_fact": "Рік заснування Одеського національного університету імені І. І. Мечникова. Відповідай лише роком.",
    "2_format": "Рік заснування Одеського національного університету імені І. І. Мечникова. JSON: name, year, city для цього університету. Без пояснень, без markdown, лише JSON.",
    "3_summary": "Стисни до двох речень, збережи всі числа: \n\n" + TEXT,
    "4_code": "is_palindrome(s), ігнорує пробіли й регістр. Лише код.",
    "5_logic": "25 студентів, 12 знають Python, 9 Java, 4 обидві. Скільки не знають жодної? Покажи хід розв'язання.",
    "6_language": "Чим стек відрізняється від черги. Поясни українською, два абзаци.",
}

PROVIDERS_TO_TEST = ["local_llama", "local_qwen", "cloud"]

try:
    with open("quality.json", "r", encoding="utf-8") as f:
        results = json.load(f)
except Exception:
    results = {}

for provider in PROVIDERS_TO_TEST:
    client, model = make_client(provider)

    if model in results and len(results[model]) == len(TASKS):
        print(f"\n[SKIP] Дані для {model} ({provider}) вже є у quality.json, пропускаємо.")
        continue

    print(f"\n>>> Запуск генерації для: {model} ({provider})")
    results[model] = {}

    for task_id, prompt in TASKS.items():
        answers = []
        print(f"  Виконуємо {task_id} (2 спроби)...")
        for attempt in range(2):
            r = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            ans = r.choices[0].message.content.strip()
            answers.append(ans)
        results[model][task_id] = answers

        with open("quality.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

print("\nВсі три моделі успішно збережено у quality.json!")