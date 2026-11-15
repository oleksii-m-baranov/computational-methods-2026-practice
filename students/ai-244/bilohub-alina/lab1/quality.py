import json
import os

from providers import make_client

# Текст для завдання 3 (варіант 1, освіта): абзац про університет на 5-6 речень
# з щонайменше трьома числами. Вставте його у файл text.txt поруч зі скриптом.
if not os.path.exists("text.txt"):
    raise SystemExit("Створіть файл text.txt і вставте в нього текст для завдання 3.")
with open("text.txt", encoding="utf-8") as f:
    TEXT = f.read().strip()
if not TEXT:
    raise SystemExit("Файл text.txt порожній.")

TASKS = {
    "1_fact":     "Рік заснування Одеського національного університету імені І. І. Мечникова. Відповідай лише роком.",
    "2_format":   "JSON: name, year, city для Одеського національного університету імені І. І. Мечникова. Без пояснень, без markdown, лише JSON.",
    "3_summary":  "Стисни наступний текст до двох речень, збережи всі числа:\n\n" + TEXT,
    "4_code":     "Напиши функцію Python is_palindrome(s), яка ігнорує пробіли й регістр. Лише код.",
    "5_logic":    "25 студентів, 12 знають Python, 9 Java, 4 обидві. Скільки не знають жодної? Покажи хід розв'язання.",
    "6_language": "Чим стек відрізняється від черги. Поясни українською, два абзаци.",
}

# (провайдер, модель; None = модель за замовчуванням із providers.py)
RUNS = [
    ("local", "llama3.2:3b"),
    ("local", "qwen3:4b"),
    ("cloud", None),
]

results = {}

for provider, model_override in RUNS:
    client, default_model = make_client(provider)
    model = model_override or default_model
    results[model] = {}
    for task_id, prompt in TASKS.items():
        answers = []
        for attempt in range(2):          # два прогони на завдання
            r = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            answers.append(r.choices[0].message.content)
        results[model][task_id] = answers
        print(f"{model} / {task_id} — готово", flush=True)

    # зберігаємо після кожної моделі, щоб нічого не втратити
    with open("quality.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

print("\n===== Перевірка завдання 2: json.loads() =====")
for model, tasks in results.items():
    for i, answer in enumerate(tasks["2_format"], 1):
        try:
            json.loads(answer)
            status = "парситься БЕЗ правок (2 бали)"
        except Exception:
            status = "НЕ парситься як є (перевірте, чи це лише обгортка ```json -> 1 бал)"
        print(f"{model}, прогон {i}: {status}")

print("\nВідповіді збережено у quality.json")
