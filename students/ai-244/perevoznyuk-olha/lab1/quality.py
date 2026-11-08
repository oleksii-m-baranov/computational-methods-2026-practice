import json
import time
from providers import make_client

TEXT = "Перший в історії публічний кінопоказ братів Люм'єр відбувся у **1895** " \
"році в Парижі, що ознаменувало народження нового мистецтва. " \
"За свою історію кінематограф пройшов шлях від німих короткометражок до " \
"масштабних блокбастерів із бюджетами понад **200** мільйонів доларів. " \
"Легендарний фільм «Володар перснів: Повернення короля» встановив історичний рекорд," \
" здобувши одразу **11** премій «Оскар». Створення якісної анімаційної стрічки" \
" зазвичай вимагає від **3** до **5** років наполегливої праці великої команди" \
" фахівців. Щороку у світовий прокат виходить понад **5000** нових художніх" \
" фільмів найрізноманітніших жанрів. Найуспішніші кінокартини здатні зібрати " \
"понад **2** мільярди доларів касових зборів, стаючи глобальними культурними " \
"феноменами."

TASKS = {
    "1_fact": "Рік першого публічного кінопоказу братів Люм’єр. Відповідай лише роком.",    
    "2_format": "JSON: event, year, city. Без пояснень, без markdown, лише JSON.",  
    "3_summary":  "Стисни наступний текст до двох речень, збережи всі числа:\n\n" + TEXT,
    "4_code":     " top_rated(films, n) — n найкращих за рейтингом. Лише код.",
    "5_logic":  "Зал 180 місць, сеанс 1 год 45 хв + 15 хв перерва, робота з 10:00 до "
    "23:00. Скільки сеансів і глядачів?. Покажи хід розв'язання.",   
    "6_language": "Чим документальне кіно відрізняється від художнього. Поясни українською, два абзаци.",
}

MODELS_TO_TEST = [
    ("local", "llama3.2:3b"),
    ("local", "qwen3:4b"),
    #("cloud", "models/gemini-3-flash-preview"),
    ("groq", "openai/gpt-oss-120b"), 
]

all_results = {}

for provider, model_name in MODELS_TO_TEST:
    print(f"\n--- Тестуємо модель: {model_name} ({provider}) ---")
    client, _ = make_client(provider)

    # Розігрів
    try:
        client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": "розігрів"}],
            timeout=60,
        )
    except Exception as e:
        print(f"Попередження при розігріві {model_name}: {e}")

    all_results[model_name] = {}

    for task_id, prompt in TASKS.items():
        answers = []
        print(f"  Завдання: {task_id}...")
        for attempt in range(2):  # два прогони
            try:
                r = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=400,
                    timeout=300,  
                )
                answers.append(r.choices[0].message.content)
            except Exception as e:
                print(f"    Помилка на спробі {attempt+1}: {e}")
                answers.append("ПОМИЛКА_ТАЙМАУТУ")

            if provider == "groq":
                time.sleep(12)

        all_results[model_name][task_id] = answers

with open("quality.json", "w", encoding="utf-8") as f:
    json.dump(all_results, f, ensure_ascii=False, indent=4)

print(
    "\nУсі тести успішно завершено! Результати збережено в новий quality.json."
)