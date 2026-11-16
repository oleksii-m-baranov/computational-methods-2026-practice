
"""ЛР №1, завдання 5: повторний прогін лише Gemini (6 завдань × 2)."""

import argparse
import json
import time
from pathlib import Path
from providers import make_client

MODEL = "gemini-3.5-flash-lite"
FILE = Path(__file__).with_name("quality.json")

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
        "Стисни наступний текст до двох речень, збережи всі числа:\n\n" + TEXT
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


def save(data):
    temp = FILE.with_suffix(".json.tmp")
    temp.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    temp.replace(FILE)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not FILE.exists():
        raise SystemExit(
            "Не знайдено quality.json. Не створюй порожній файл!"
        )

    data = json.loads(FILE.read_text(encoding="utf-8"))

    if not all(
        isinstance(data.get(m), dict)
        for m in ("llama3.2:3b", "qwen3:4b")
    ):
        raise SystemExit(
            "У quality.json немає результатів двох локальних моделей"
        )

    cloud = data.get(MODEL, {})

    if not isinstance(cloud, dict):
        raise SystemExit(
            "Неправильна структура відповідей Gemini"
        )

    for task in TASKS:
        answers = cloud.get(task, [])
        if not isinstance(answers, list) or len(answers) > 2:
            raise SystemExit(f"Некоректні дані: {task}")

    completed = sum(
        len(cloud.get(task, [])) for task in TASKS
    )

    print(
        f"Модель {MODEL}: готово {completed}/12 відповідей"
    )
    print("Локальні моделі повторно НЕ запускаємо")

    if args.dry_run:
        print(
            "DRY RUN OK: запитів до Google не було; "
            "файли не змінено"
        )
        return

    client, model = make_client("cloud")

    if model != MODEL:
        raise SystemExit(
            "У providers.py вказана інша хмарна модель"
        )

    data[MODEL] = cloud

    for task, prompt in TASKS.items():
        answers = cloud.setdefault(task, [])

        while len(answers) < 2:
            print(
                f"{task} — спроба {len(answers) + 1}/2",
                flush=True
            )

            try:
                r = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                )

                answer = r.choices[0].message.content

                if not isinstance(answer, str) or not answer.strip():
                    raise ValueError(
                        "Модель повернула порожню відповідь"
                    )

            except KeyboardInterrupt:
                print(
                    "\nЗупинено. Успішні відповіді вже збережені"
                )
                return

            except Exception as exc:
                status = getattr(exc, "status_code", None)

                if (
                    status == 429
                    or "RESOURCE_EXHAUSTED" in str(exc)
                ):
                    print(
                        "Ліміт API 429. "
                        "Помилку НЕ записано як відповідь"
                    )
                else:
                    print(
                        f"Помилка запиту: "
                        f"{type(exc).__name__} (HTTP {status})"
                    )

                print(
                    "Повтори команду пізніше — програма "
                    "продовжить із цього місця"
                )
                return

            answers.append(answer)
            save(data)

            print("  Відповідь збережено")
            time.sleep(5)

    # Видаляємо старий запис Gemini лише після 12 успішних відповідей.
    data.pop("gemini-3.8-flash", None)
    save(data)

    print(
        "Готово: 12/12. "
        "Відкрий quality.json і оціни відповіді за рубрикою"
    )


if __name__ == "__main__":
    main()
