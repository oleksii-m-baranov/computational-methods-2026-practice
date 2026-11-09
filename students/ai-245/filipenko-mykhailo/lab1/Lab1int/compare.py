
import csv
import json
import time

from providers import PROVIDERS, make_client

# Варіант 9
TASKS = [
    {
        "id": "Q1",
        "prompt": "Поясни різницю між функцією і методом у Python. Наведи короткий приклад."
    },
    {
        "id": "Q2",
        "prompt": "Космічний апарат летить 480 млн км зі швидкістю 60 000 км/год. Скільки годин і діб триватиме політ?"
    },
    {
        "id": "Q3",
        "prompt": "Поясни різницю між зіркою та планетою. Коротко."
    }
]

SYSTEM = "Відповідай українською мовою, чітко та по суті."

results = []

for task in TASKS:
    for provider, config in PROVIDERS.items():
        print(f"\nЗавдання: {task['id']}")
        print(f"Модель: {config['model']}")
        print("Очікуємо відповідь...")

        try:
            client = make_client(provider)
            start = time.perf_counter()

            response = client.chat.completions.create(
                model=config["model"],
                messages=[
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": task["prompt"]}
                ],
                temperature=0.3,
                max_tokens=4096
            )

            seconds = round(time.perf_counter() - start, 2)
            answer = response.choices[0].message.content or ""

            usage = response.usage
            prompt_tokens = usage.prompt_tokens if usage else 0
            completion_tokens = usage.completion_tokens if usage else 0

            result = {
                "task": task["id"],
                "provider": provider,
                "model": config["model"],
                "answer": answer,
                "seconds": seconds,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "status": "ok" if answer.strip() else "empty"
            }

        except Exception as error:
            result = {
                "task": task["id"],
                "provider": provider,
                "model": config["model"],
                "answer": "",
                "seconds": 0,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "status": f"error: {error}"
            }

        results.append(result)

        print("Статус:", result["status"])
        print("Час:", result["seconds"], "с")
        print("Відповідь:", result["answer"][:300])

with open("compare_results.json", "w", encoding="utf-8") as file:
    json.dump(results, file, ensure_ascii=False, indent=2)

with open("compare_results.csv", "w", newline="", encoding="utf-8-sig") as file:
    writer = csv.DictWriter(file, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)

print("\nПорівняння завершено!")
print("Збережено compare_results.json і compare_results.csv")
