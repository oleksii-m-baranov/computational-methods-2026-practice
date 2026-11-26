from providers import make_client
import json

TEXT = """В Україні є понад 300 університетів та інших закладів вищої освіти, де навчаються багато студентів. Зазвичай навчання на бакалавра триває 4 роки. Після цього можна піти в магістратуру ще на 1,5–2 роки. У багатьох університетах є 5–10 факультетів. Студенти відвідують пари, виконують лабораторні роботи та складають іспити протягом 2 семестрів на рік. Також вони можуть брати участь у різних проєктах, конференціях та програмах обміну."""

TASKS = {
    "1_fact":     "Рік заснування Одеського національного університету імені І. І. Мечникова. Відповідай лише роком.",
    "2_format":   "JSON: name, year, city для цього університету. Без пояснень, без markdown, лише JSON.",
    "3_summary":  "Стисни наступний текст до двох речень, збережи всі числа:\n\n" + TEXT,
    "4_code":     "is_palindrome(s), ігнорує пробіли й регістр. Лише код.",
    "5_logic":    "25 студентів, 12 знають Python, 9 Java, 4 обидві. Скільки не знають жодної?. Покажи хід розв'язання.",
    "6_language": "Чим стек відрізняється від черги. Поясни українською, два абзаци.",
}

results = {}

for provider in ["local1", "local2", "cloud"]:
    client, model = make_client(provider)
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
        print(f"{model} / {task_id} — готово")

with open("quality.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)