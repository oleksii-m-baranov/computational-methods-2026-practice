from providers import make_client
import json
import os
import requests

TEXT = """Перший iPhone надійшов у продаж у США 29 червня 2007 року.
Apple пропонувала модель із 4 ГБ пам’яті за 499 доларів і модель із 8 ГБ за 599 доларів.
Смартфон мав 3,5-дюймовий сенсорний дисплей.
Заявлений час розмови становив до 8 годин.
Пристрій поєднував функції мобільного телефона, музичного плеєра iPod і засобу доступу до Інтернету."""

TASKS = {
    "1_fact": "Рік випуску першого iPhone. Відповідай лише роком.",
    "2_format": "Надай дані про перший iPhone у форматі JSON з полями product, year, company. Без пояснень, без markdown, лише JSON.",
    "3_summary": "Стисни наступний текст до двох речень, збережи всі числа:\n\n" + TEXT,
    "4_code": "Напиши функцію average_grade(grades), яка обчислює середню оцінку після видалення однієї найнижчої оцінки зі списку. Лише код.",
    "5_logic": "Сервер обробляє 1200 запитів/хв, 15% дають помилку, з них 40% повторюються успішно. Скільки запитів втрачено за годину? Покажи хід розв'язання.",
    "6_language": "Чим оперативна пам’ять відрізняється від жорсткого диска? Поясни українською, два абзаци.",
}

if os.path.exists("quality.json"):
    with open("quality.json", "r", encoding="utf-8") as f:
        results = json.load(f)
else:
    results = {}

for provider in ["local", "qwen", "cloud"]:
    client, model = make_client(provider)

    if provider != "qwen":
        client = client.with_options(timeout=600.0, max_retries=0)

    if model not in results:
        results[model] = {}

    for task_id, prompt in TASKS.items():

        if task_id not in results[model]:
            results[model][task_id] = []

        answers = results[model][task_id]

        while len(answers) < 2:
            attempt = len(answers) + 1

            print(f"{model} / {task_id} / спроба {attempt} — запуск...")

            try:
                if provider == "qwen":
                    response = requests.post(
                        "http://localhost:11434/api/chat",
                        json={
                            "model": model,
                            "messages": [
                                {
                                    "role": "user",
                                    "content": prompt
                                }
                            ],
                            "think": False,
                            "stream": False,
                            "options": {
                                "num_predict": 2048,
                                "temperature": 0.7
                            }
                        },
                        timeout=900
                    )

                    response.raise_for_status()
                    answer = response.json()["message"]["content"]

                else:
                    r = client.chat.completions.create(
                        model=model,
                        messages=[
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        temperature=0.7,
                    )

                    answer = r.choices[0].message.content

                answers.append(answer)

                with open("quality.json", "w", encoding="utf-8") as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)

                print(
                    f"{model} / {task_id} / спроба {attempt} — готово і збережено"
                )

            except Exception as e:
                print(f"ПОМИЛКА: {e}")
                print(
                    "Усе, що було виконано раніше, вже збережене у quality.json."
                )
                raise

print("УСЕ ГОТОВО")