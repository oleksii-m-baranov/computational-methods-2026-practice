
import json
import time
import urllib.request
import csv

URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:3b"

TASKS = [
    ("task1", "У якому році відкрили Київський метрополітен?"),
    ("task2", 'Поверни ТІЛЬКИ валідний JSON без markdown та пояснень у форматі {"city": "...", "year": ..., "lines_count": ...} для Києва.'),
    ("task3", "Стисни текст до двох речень, зберігши всі числові значення: У 2024 році компанія перевезла 12500 тонн вантажу, виконавши 840 рейсів із 37 міст."),
    ("task4", "Напиши функцію total_weight(items), яка приймає список словників із ключем weight і повертає суму всіх ваг. Використай Python."),
    ("task5", "Є 120 коробок. 45 коробок важать по 8 кг, решта — по 12 кг. Вантажівка може перевозити не більше 1200 кг. Скільки рейсів потрібно зробити?"),
    ("task6", "Поясни двома абзацами різницю між контейнерними та навалочними перевезеннями. Відповідай українською.")
]

results = []

for task_id, prompt in TASKS:
    print(f"\nВиконується {task_id}...")
    data = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0}
    }

    start = time.perf_counter()
    try:
        request = urllib.request.Request(
            URL,
            data=json.dumps(data, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(request, timeout=180) as response:
            result = json.loads(response.read().decode("utf-8"))

        row = {
            "model": MODEL,
            "task": task_id,
            "prompt": prompt,
            "response": result.get("response", ""),
            "total_seconds": round(time.perf_counter() - start, 2),
            "generation_seconds": round(result.get("eval_duration", 0) / 1e9, 2),
            "tokens": result.get("eval_count", 0),
            "status": "success"
        }
        print("Час:", row["total_seconds"], "с")
        print("Відповідь:", row["response"][:300].replace("\n", " "))

    except Exception as error:
        row = {
            "model": MODEL,
            "task": task_id,
            "prompt": prompt,
            "response": "",
            "total_seconds": round(time.perf_counter() - start, 2),
            "generation_seconds": 0,
            "tokens": 0,
            "status": f"error: {error}"
        }
        print("Помилка:", error)

    results.append(row)

with open("task5_llama_results.json", "w", encoding="utf-8") as file:
    json.dump(results, file, ensure_ascii=False, indent=2)

with open("task5_llama_results.csv", "w", encoding="utf-8-sig", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)

print("\nГотово. Результати збережено у task5_llama_results.json і task5_llama_results.csv")
