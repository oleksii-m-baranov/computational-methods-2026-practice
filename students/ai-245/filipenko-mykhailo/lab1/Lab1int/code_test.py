import json
from urllib.request import Request, urlopen

MODELS = ["llama3.2:3b", "qwen3:4b"]

PROMPT = """
Напиши функцію Python light_travel_time(distance_km),
яка обчислює час проходження світлом заданої
відстані в кілометрах.

Використай швидкість світла 299792.458 км/с.
Результат поверни в секундах.

Дай коротке пояснення роботи функції.
"""

def ask_model(model, prompt):
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3
        }
    }

    request = Request(
        "http://localhost:11434/api/generate",
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    with urlopen(request, timeout=300) as response:
        result = json.loads(response.read().decode("utf-8"))

    return result["response"]


results = []

for model in MODELS:
    print(f"\nМодель: {model}")
    print("Очікуємо відповідь...\n")

    answer = ask_model(model, PROMPT)

    print("Відповідь моделі:")
    print(answer)

    results.append({
        "model": model,
        "task": "light_travel_time(distance_km)",
        "answer": answer
    })


with open("code_results.json", "w", encoding="utf-8") as file:
    json.dump(results, file, ensure_ascii=False, indent=4)

print("\nТестування завершено!")
print("Результати збережено у code_results.json")
