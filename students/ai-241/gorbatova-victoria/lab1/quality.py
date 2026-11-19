# -*- coding: utf-8 -*-
import json
import time
from providers import make_client

# Текст для Завдання 3 (Варіант 7: Кіно / Одеський оперний театр)
TEXT = """В Одесі на вулиці Чайковського розташований знаменитий Одеський національний академічний театр опери та балету, нинішню будівлю якого було відкрито у 1887 році. Зал театру має унікальну акустику і вміщує 1636 глядачів. Поруч із театром у 1896 році відбулися перші в місті кінопокази, які зібрали понад 400 глядачів за перший тиждень. За свою історію будівля пережила масштабну реконструкцію, яка тривала з 1996 по 2007 рік і коштувала понад 30 мільйонів доларів. Сьогодні театр залишається однією з найвідоміших архітектурних пам'яток України, приймаючи понад 200 вистав на рік."""

TASKS = {
    "1_fact": "В якому році відбувся перший публічний кінопоказ братів Люм'єр? Відповідай лише роком.",
    "2_format": 'Згенеруй JSON із полями "landmark" (Одеський оперний театр), "city" (Одеса) та "year" (1887). Без пояснень, без markdown, лише JSON.',
    "3_summary": "Стисни наступний текст до двох речень, збережи всі числа:\n\n" + TEXT,
    "4_code": "Напиши функцію top_rated(films, n) на Python, яка приймає список словників фільмів (із ключами 'title' та 'rating') і повертає n найкращих за рейтингом. Лише код.",
    "5_logic": "Кінозал має 180 місць. Один сеанс триває 1 годину 45 хвилин, після нього є 15 хвилин перерви. Кінотеатр працює з 10:00 до 23:00. Скільки всього сеансів можна провести за день і скільки максимум глядачів зможуть їх відвідати при 100% заповнюваності? Покажи хід розв'язання.",
    "6_language": "Чим документальне кіно відрізняється від художнього? Поясни українською, два абзаци."
}

MODELS_TO_TEST = [
    ("local", "llama3.2:3b"),
    ("local", "qwen3:4b"),
    ("cloud", "gemini-3.8-flash")
]

results = {}

for provider, model_name in MODELS_TO_TEST:
    try:
        client, model = make_client(provider)
        target_model = model_name if provider == "local" else model
        results[target_model] = {}
        
        print(f"\n--- Тестування {target_model} ---")
        for task_id, prompt in TASKS.items():
            answers = []
            for attempt in range(2):
                if provider == "cloud":
                    time.sleep(13) 
                
                r = client.chat.completions.create(
                    model=target_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                )
                answers.append(r.choices[0].message.content)
            results[target_model][task_id] = answers
            print(f"{target_model} / {task_id} — готово")
    except Exception as e:
        print(f"Помилка при тестуванні {model_name}: {e}")

# Збереження відповідей у JSON
with open("quality.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\nУсі тестування завершено! Результати збережено у quality.json")