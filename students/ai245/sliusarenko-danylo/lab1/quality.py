import time
import json
from providers import make_client

# Текст для Завдання 3 (Варіант 4 - Спорт: 5 речень, 4 конкретні числа)
TEXT = """Перші сучасні Олімпійські ігри відбулися у 1896 році в Афінах. У змаганнях узяв участь 241 спортсмен виключно чоловічої статі. Учасники представляли 14 країн світу на цих відновлених змаганнях. Загалом було розіграно 43 комплекти нагород у 9 видах спорту. Найбільшу кількість медалей тоді здобула збірна Греції."""

TASKS = {
    "1_fact": "Рік перших сучасних Олімпійських ігор? Відповідай лише роком.",
    "2_format": 'JSON з полями "event", "year", "city" для перших сучасних Олімпійських ігор. Без пояснень, без markdown, лише JSON.',
    "3_summary": f"Стисни наступний текст до двох речень, збережи всі числа:\n\n{TEXT}",
    "4_code": 'Напиши функцію win_rate(results), яка приймає список результатів матчів зі значеннями "W", "L", "D" та повертає відсоток перемог. Лише код.',
    "5_logic": "8 команд, кожна з кожною по разу. Скільки матчів? При 4 матчах на день — скільки днів? Покажи хід розв'язання.",
    "6_language": "Чим спринт відрізняється від стаєрського бігу? Поясни українською, два абзаци.",
}

results = {}

for provider_name in ["llama", "qwen", "cloud"]:
    client, model = make_client(provider_name)
    results[model] = {}
    print(f"\n--> Тестуємо модель: {model}...")

    for task_id, prompt in TASKS.items():
        answers = []
        for attempt in range(2):
            try:
                r = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                )
                answers.append(r.choices[0].message.content)
            except Exception as e:
                print(f"Помилка запиту: {e}")
                answers.append(f"ERROR: {e}")

            if provider_name == "cloud":
                time.sleep(4)  # Пауза для запобігання RateLimit на Gemini

        results[model][task_id] = answers
        print(f"    {model} / {task_id} — готово")

with open("quality.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\nВсі тести завершено! Результати збережено у quality.json")