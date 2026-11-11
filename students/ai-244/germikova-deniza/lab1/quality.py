
from providers import make_client
import json
import time

TEXT = """Київський метрополітен відкрили 1960 року.
Нині метро має 3 лінії та 52 станції.
Загальна довжина ліній становить приблизно 69,6 км.
Метрополітен щодня перевозить велику кількість пасажирів.
Станції метро забезпечують пересадки між різними лініями та іншими видами транспорту."""

TASKS = {
    "1_fact": (
        "У якому році відкрили Київський метрополітен? "
        "Відповідай лише роком."
    ),

    "2_format": (
        "Створи JSON-об'єкт про Київський метрополітен із полями "
        "city, year, lines_count. Без пояснень, без markdown, "
        "лише JSON."
    ),

    "3_summary": (
        "Стисни наступний текст до двох речень, збережи всі числа:\n\n"
        + TEXT
    ),

    "4_code": (
        "Напиши функцію total_weight(items), яка обчислює сумарну вагу "
        "предметів зі списку словників. У кожному словнику є ключ "
        "'weight' із числовим значенням ваги. Функція має повернути "
        "суму всіх ваг. Лише код."
    ),

    "5_logic": (
        "Є 120 ящиків. Із них 45 ящиків важать по 8 кг кожен, "
        "а решта — по 12 кг кожен. Вантажівка може перевозити "
        "не більше 1200 кг за один рейс. Скільки мінімум рейсів "
        "потрібно, щоб перевезти всі ящики? Покажи хід розв'язання."
    ),

    "6_language": (
        "Поясни, чим контейнерне перевезення відрізняється від "
        "навалочного перевезення вантажів. Поясни українською, "
        "у двох змістовних абзацах."
    ),
}

results = {}

for provider, selected_model in [
    ("local", "llama3.2:3b"),
    ("local", "qwen3:4b"),
    ("cloud", None),
]:
    client, model = make_client(provider)

    if selected_model is not None:
        model = selected_model
    results[model] = {}

    for task_id, prompt in TASKS.items():
        answers = []

        for attempt in range(2):
            for retry in range(3):
                try:
                    r = client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7,
                    )

                    answers.append(r.choices[0].message.content)
                    break

                except Exception as e:
                    if retry == 2:
                        print(f"{model} / {task_id} — помилка: {e}")
                        answers.append(f"ERROR: {e}")
                    else:
                        print(
                            f"{model} / {task_id} — повторна спроба "
                            f"{retry + 1}/2 через 5 секунд"
                        )
                        time.sleep(5)

        results[model][task_id] = answers

        with open("quality.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"{model} / {task_id} — готово")

print("\nРезультати збережено у quality.json")

