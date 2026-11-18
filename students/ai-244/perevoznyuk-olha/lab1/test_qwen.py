import csv
import time
from providers import make_client

TEXT = (
    "Перший в історії публічний кінопоказ братів Люм'єр відбувся у **1895** "
    "році в Парижі, що ознаменувало народження нового мистецтва. "
    "За свою історію кінематограф пройшов шлях від німих короткометражок до "
    "масштабних блокбастерів із бюджетами понад **200** мільйонів доларів. "
    "Легендарний фільм «Володар перснів: Повернення короля» встановив історичний рекорд, "
    "здобувши одразу **11** премій «Оскар». Створення якісної анімаційної стрічки "
    "зазвичай вимагає від **3** до **5** років наполегливої праці великої команди "
    "фахівців. Щороку у світовий прокат виходить понад **5000** нових художніх "
    "фільмів найрізноманітніших жанрів. Найуспішніші кінокартини здатні зібрати "
    "понад **2** мільярди доларів касових зборів, стаючи глобальними культурними "
    "феноменами."
)

TASKS = {
    "1_fact": "Рік першого публічного кінопоказу братів Люм’єр. Відповідай лише роком.",
    "2_format": "JSON: event, year, city. Без пояснень, без markdown, лише JSON.",
    "3_summary": "Стисни наступний текст до двох речень, збережи всі числа:\n\n"
    + TEXT,
    "4_code": " top_rated(films, n) — n найкращих за рейтингом. Лише код.",
    "5_logic": (
        "Зал 180 місць, сеанс 1 год 45 хв + 15 хв перерва, робота з 10:00 до"
        " 23:00. Скільки сеансів і глядачів?. Покажи хід розв'язання."
    ),
    "6_language": (
        "Чим документальне кіно відрізняється від художнього. Поясни українською,"
        " два абзаци."
    ),
}

model_name = "qwen3:4b"
provider = "local"

client, _ = make_client(provider)
new_rows = []

print(f"Починаємо тестування моделі: {model_name}")

# Прогрів моделі
try:
    client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": "розігрів"}],
        timeout=120.0,
    )
except Exception as e:
    print(f"Помилка при запуску моделі: {e}")
    exit()

for task_id, prompt in TASKS.items():
    answers = []
    print(f"Обробка завдання: {task_id}...")
    for attempt in range(2):  # два прогони на завдання
        try:
            r = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=400,  # Захист від нескінченної генерації
                timeout=120.0,  # Таймаут 60 секунд на один запит
            )
            answers.append(r.choices[0].message.content)
        except Exception as e:
            print(f"  [Помилка/Таймаут на спробі {attempt+1}]: {e}")
            answers.append("ПОМИЛКА_ТАЙМАУТУ")

    new_rows.append({"model": model_name, "task": task_id, "answers": answers})
    print(f"{model_name} / {task_id} — готово")

with open("results.csv", "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for row in new_rows:
        # Записуємо у файл (тут ви можете адаптувати під формат вашої таблиці)
        writer.writerow(
            [provider, model_name, row["task"], str(row["answers"])]
        )

print("Тестування Qwen завершено успішно!")