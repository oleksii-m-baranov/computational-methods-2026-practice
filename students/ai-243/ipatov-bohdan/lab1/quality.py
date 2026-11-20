import json
import time
from providers import make_client

# Factual paragraph about ONU Mechnikov with verified numeric data
TEXT = (
    "Одеський національний університет імені І. І. Мечникова засновано 13 травня 1865 року "
    "на базі Рішельєвського ліцею. На момент відкриття в ньому навчалося 175 студентів на трьох факультетах. "
    "Сьогодні університет налічує 11 факультетів та навчально-наукових інститутів, де здобувають освіту понад 7500 студентів. "
    "За роки існування заклад підготував понад 100 тисяч висококваліфікованих фахівців. "
    "Наукова бібліотека університету володіє унікальним фондом, який нараховує понад 3.8 мільйона видань."
)

TASKS = {
    "1_fact": "Рік заснування Одеського національного університету імені І. І. Мечникова. Відповідай лише роком.",
    "2_format": "Створи JSON: name, year, city для Одеського національного університету імені І. І. Мечникова. Без пояснень, без markdown, лише JSON.",
    "3_summary": "Стисни наступний текст до двох речень, збережи всі числа:\n\n" + TEXT,
    "4_code": "Напиши функцію is_palindrome(s), яка перевіряє, чи є рядок паліндромом, ігноруючи пробіли й регістр символів. Лише код.",
    "5_logic": "25 студентів, 12 знають Python, 9 Java, 4 обидві. Скільки не знають жодної? Покажи хід розв'язання.",
    "6_language": "Чим стек відрізняється від черги. Поясни українською, два абзаци.",
}

results = {}

for provider in ["local", "local2", "cloud"]:
    client, model = make_client(provider)
    print(f"\nRunning quality benchmark on {provider} ({model})...")
    results[model] = {}

    for task_id, prompt in TASKS.items():
        answers = []
        for attempt in range(2):  # 2 attempts per task
            for retry in range(3):
                try:
                    kwargs = {
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.7,
                    }
                    if provider == "cloud":
                        kwargs["max_tokens"] = 600

                    r = client.chat.completions.create(**kwargs)
                    answers.append(r.choices[0].message.content or "")
                    break
                except Exception as e:
                    print(f"  Retry {retry+1} for {model}/{task_id}: {e}")
                    time.sleep(5)
            time.sleep(1)

        results[model][task_id] = answers
        print(f"  {model} / {task_id} completed (attempts: {len(answers)})")

with open("quality.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\nSaved quality results to quality.json")
