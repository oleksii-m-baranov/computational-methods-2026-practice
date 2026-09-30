import json

from dotenv import load_dotenv
from providers import make_client

load_dotenv()

# Текст для завдання 3 (Стиснення) за темою "Спорт" (варіант 4)
TEXT = (
    "Сучасні Олімпійські ігри беруть свій початок з 1896 року, коли в Афінах відбулися перші змагання. "
    "У тих історичних іграх взяв участь 241 спортсмен, які представляли 14 країн світу. "
    "Програма першої олімпіади налічувала 43 види спорту в 9 спортивних дисциплінах. "
    "Згодом масштаби турніру колосально зросли. На літніх іграх у Токіо брало участь вже понад 11 тисяч атлетів із 206 держав. "
    "Сучасний цикл проведення олімпіад складає рівно 4 роки між літніми або зимовими іграми."
)

TASKS = {
    "1_fact": "Який рік перших сучасних Олімпійських ігор? Відповідай лише роком.",
    "2_format": "Надай інформацію про перші сучасні Олімпійські ігри у форматі JSON із ключами: event, year, city. Без пояснень, без markdown-обгорток.",
    "3_summary": "Стисни наступний текст до двох речень, зберігши всі числа:\n\n"
    + TEXT,
    "4_code": "Напиши функцію win_rate(results) на Python, яка приймає список рядків 'W', 'L', 'D' та повертає відсоток перемог (кількість 'W' поділити на загальну кількість елементів помножити на 100). Лише код.",
    "5_logic": "У турнірі беруть участь 8 команд, кожна грає з кожною по разу. Скільки всього буде матчів? Якщо гратимуть по 4 матчі на день, скільки днів триватиме турнір? Покажи хід розв'язання.",
    "6_language": "Чим спринт відрізняється від стаєрського бігу? Поясни українською мовою у двох абзацах.",
}

results = {}

# Перелік провайдерів для тестування (включаючи твою локальну та хмарну моделі)
providers_to_test = [
    ("local", "llama3.2:3b"),
    ("local", "qwen3:4b"),  # <--- ДОДАЙ ОСЬ ЦЕЙ РЯДОК
    ("cloud", "qwen/qwen3.8-27b"),  # або інша хмарна модель, яку ти налаштував
]

for provider_key, model_name in providers_to_test:
    client, model = make_client(provider_key)
    # Якщо використовуєш OpenRouter чи іншу хмару, переконайся у правильних параметрах make_client
    results[model_name] = {}
    print(f"\nТестуємо модель: {model_name}...")

    for task_id, prompt in TASKS.items():
        answers = []
        for attempt in range(2):  # два прогони для перевірки детермінованості
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            ans = response.choices[0].message.content.strip()
            answers.append(ans)

        results[model_name][task_id] = answers
        print(f"  - Завдання {task_id} готово.")

with open("quality.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\nУспіх! Результати збережено у файл quality.json")
