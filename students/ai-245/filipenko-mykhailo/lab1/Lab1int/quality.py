import json
import time
from providers import make_client, PROVIDERS


TEXT = """
12 квітня 1961 року Юрій Гагарін став першою людиною,
яка здійснила орбітальний космічний політ.
Він перебував на борту корабля «Восток-1».
Космічний корабель рухався зі швидкістю
27400 кілометрів на годину.
Політ тривав 108 хвилин.
Максимальна висота польоту становила приблизно
327 кілометрів над поверхнею Землі.
"""

TASKS = {
    "1_fact": (
        "У якому році відбувся перший політ людини "
        "в космос? Відповідай лише роком."
    ),
    "2_json": (
        "Подай інформацію про перший політ людини "
        "в космос у форматі JSON з полями "
        "event, year, person. Лише JSON."
    ),
    "3_summary": (
        "Стисни текст до двох речень, збережи всі числа:\n"
        + TEXT
    ),
    "4_code": (
        "Напиши функцію Python "
        "light_travel_time(distance_km), "
        "яка повертає час проходження світлом "
        "відстані в секундах. "
        "Швидкість світла — 299792.458 км/с."
    ),
    "5_logic": (
        "Зонд летить зі швидкістю 60000 км/год. "
        "Відстань — 480000000 км. "
        "Скільки повних діб триватиме політ? "
        "Покажи обчислення."
    ),
    "6_language": (
        "Поясни українською різницю між зорею "
        "та планетою. Відповідь — два абзаци."
    )
}

MODELS = [
    ("llama", "llama3.2:3b"),
    ("qwen", "qwen3:4b"),
    ("cloud", "gemini-3.5-flash-lite")
]

results = {}

for provider, model in MODELS:
    print(f"\nМодель: {model}")

    client = make_client(provider)
    results[model] = {}

    for task_id, prompt in TASKS.items():
        results[model][task_id] = []

        for run in range(1, 3):
            print(
                f"Завдання {task_id}, "
                f"прогін {run}/2..."
            )

            start = time.perf_counter()

            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.7,
                    max_tokens=4096
                )

                answer = (
                    response.choices[0].message.content
                    or ""
                )

                finish_reason = (
                    response.choices[0].finish_reason
                )

                status = (
                    "ok" if answer.strip() else "empty"
                )
                error = None

            except Exception as exc:
                answer = ""
                finish_reason = None
                status = "error"
                error = str(exc)

            seconds = round(
                time.perf_counter() - start, 2
            )

            item = {
                "run": run,
                "answer": answer,
                "status": status,
                "seconds": seconds,
                "finish_reason": finish_reason,
                "error": error
            }

            results[model][task_id].append(item)

            with open(
                "quality.json",
                "w",
                encoding="utf-8"
            ) as file:
                json.dump(
                    results,
                    file,
                    ensure_ascii=False,
                    indent=2
                )

            print(
                f"Статус: {status}, "
                f"час: {seconds} с"
            )

print("\nГотово! Результати у quality.json")
