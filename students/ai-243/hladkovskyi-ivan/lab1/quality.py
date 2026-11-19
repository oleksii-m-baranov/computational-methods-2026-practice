import json
import os
import time
from providers import make_client

# Текст для завдання 3 (джерело: Вікіпедія, «Брати Люм'єр» / «Кінематограф»).
TEXT = """28 грудня 1895 року в Парижі, у залі Гран-кафе на бульварі Капуцинок, брати Огюст і Луї Люм'єр провели перший платний публічний кінопоказ. Квиток коштував 1 франк. У першому сеансі глядачі побачили програму приблизно з десяти коротких фільмів, кожен тривалістю близько 50 секунд. Серед них був знаменитий «Прибуття потяга на вокзал Ла-Сьота». Апарат братів, кінематограф, був запатентований у лютому 1895 року. Уже за кілька місяців сеанси відбувалися в багатьох країнах світу."""

TASKS = {
    "1_fact": "Рік першого публічного кінопоказу братів Люм'єр. Відповідай лише роком.",
    "2_format": "Рік першого публічного кінопоказу братів Люм'єр. JSON: event, year, city. Без пояснень, без markdown, лише JSON.",
    "3_summary": "Стисни наступний текст до двох речень, збережи всі числа:\n\n" + TEXT,
    "4_code": "top_rated(films, n) — повертає n найкращих фільмів за рейтингом. Лише код.",
    "5_logic": "Зал 180 місць, сеанс 1 год 45 хв + 15 хв перерва, робота з 10:00 до 23:00. Скільки сеансів і глядачів? Покажи хід розв'язання.",
    "6_language": "Чим документальне кіно відрізняється від художнього. Поясни українською, два абзаци.",
}

PROVIDER_LIST = ["local_llama", "local_qwen", "cloud"]


def ask(client, model, prompt, retries=4):
    for i in range(retries):
        try:
            r = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            return r.choices[0].message.content
        except Exception as e:  # 429 та мережеві збої
            print(f"  помилка: {e}; повтор {i + 1}/{retries} через 20 с")
            time.sleep(20)
    raise RuntimeError("не вдалося отримати відповідь")


# не затираємо вже зібране: дописуємо до існуючого quality.json
results = {}
if os.path.exists("quality.json"):
    with open("quality.json", encoding="utf-8") as f:
        results = json.load(f)

for provider in PROVIDER_LIST:
    client, model = make_client(provider)
    results[model] = {}
    for task_id, prompt in TASKS.items():
        answers = [ask(client, model, prompt) for _ in range(2)]  # два прогони
        results[model][task_id] = answers
        print(f"{model} / {task_id} — готово")
        with open("quality.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

# Завдання 2: автоматична перевірка json.loads()
print("\n--- json.loads() для завдання 2 ---")
for model, tasks in results.items():
    for i, ans in enumerate(tasks["2_format"], 1):
        try:
            json.loads(ans)
            print(f"{model} / прогін {i}: парситься без правок")
        except json.JSONDecodeError as e:
            print(f"{model} / прогін {i}: НЕ парситься ({e})")
