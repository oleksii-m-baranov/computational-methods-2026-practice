from providers import make_client
import json
import time

TEXT = """Гривня була введена в обіг у період з 2 до 11 вересня 1996 року 
згідно з Указом Президента України Леоніда Кучми «Про грошову реформу в Україні». 
Код валюти за стандартом ISO 4217 — UAH, цифровий код — 980. 
Під час реформи обмін проводився за курсом 100 000 карбованців за 1 гривню. 
Емітентом національної валюти є Національний банк України."""

TASKS = {
    "1_fact": "Рік уведення гривні як національної валюти. Відповідай лише роком.",
    "2_format": "Надай JSON з полями currency, code, year для національної валюти України (гривні). Без пояснень, без markdown, лише JSON.",
    "3_summary": "Стисни наступний текст до двох речень, збережи всі числа:\n\n" + TEXT,
    "4_code": "Напиши функцію compound_interest(principal, rate, years), яка розраховує складні відсотки. Лише код.",
    "5_logic": "Депозит 20000 грн під 12% річних, податок 19,5% з відсотків. Скільки грошей буде на руках через рік з урахуванням податку? Покажи хід розв'язання.",
    "6_language": "Поясни українською мовою, чим акція відрізняється від облігації. Дай відповідь двома абзацами.",
}

# Якщо файл вже частково зберігся, можна спробувати завантажити або почати з нуля
results = {}

for provider in ["local", "cloud"]:
    client, model = make_client(provider)
    results[model] = {}
    print(f"=== Тестуємо модель: {model} ===")

    for task_id, prompt in TASKS.items():
        answers = []
        for attempt in range(2):  # два прогони
            r = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            answers.append(r.choices[0].message.content)

            # Для хмари робимо паузу між запитами, щоб уникнути ліміту 429
            if provider == "cloud":
                time.sleep(12)

        results[model][task_id] = answers
        print(f"  {task_id} — готово")

with open("quality.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\nРезультати успішно збережено у quality.json!")