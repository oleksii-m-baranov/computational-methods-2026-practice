from providers import make_client
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

TEXT = """Всесвітня організація охорони здоров'я (ВООЗ) була заснована 7 квітня 1948 року і на сьогодні об'єднує 194 країни-члени. Штаб-квартира розташована в Женеві, Швейцарія. За даними ВООЗ, щороку у світі реєструється близько 1 мільярда випадків сезонного грипу, з яких 3–5 мільйонів мають тяжкий перебіг. За оцінками організації, щорічно від респіраторних захворювань помирає від 290 до 650 тисяч людей. ВООЗ також координує боротьбу з 20+ глобальними епідеміями одночасно."""

TASKS = {
    "1_fact": "Рік відкриття пеніциліну Флемінгом. Відповідай лише роком.",
    "2_format": 'JSON: discovery, year, scientist. Без пояснень, без markdown, лише JSON.',
    "3_summary": "Стисни наступний текст до двох речень, збережи всі числа:\n\n" + TEXT,
    "4_code": "Напиши функцію bmi(weight_kg, height_m), яка повертає кортеж (bmi, категорія). Категорії: <18.5 — 'underweight', 18.5-25 — 'normal', 25-30 — 'overweight', >=30 — 'obese'. Лише код.",
    "5_logic": "40 пацієнтів, 18 з температурою, 15 з кашлем, 7 з обома. У скількох немає симптомів? Покажи хід розв'язання.",
    "6_language": "Чим вірус відрізняється від бактерії. Поясни українською, два абзаци.",
}

results = {}

for provider in ["local", "local_qwen", "cloud"]:
    client, model = make_client(provider)
    results[model] = {}
    for task_id, prompt in TASKS.items():
        answers = []
        for attempt in range(2):
            try:
                r = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    timeout=900,  # 15 хвилин на запит
                )
                answers.append(r.choices[0].message.content)
            except Exception as e:
                answers.append(f"[ПОМИЛКА: {type(e).__name__}: {e}]")
                print(f"  ! {model} / {task_id} / спроба {attempt+1}: {type(e).__name__}")
        results[model][task_id] = answers
        print(f"{model} / {task_id} — готово")

    # зберігаємо після кожної моделі
    with open("quality.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  → {model} збережено в quality.json")

print("\nВсе завершено. Результати в quality.json")
