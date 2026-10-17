import json
import time
from urllib.request import Request, urlopen

# Варіант 9
PROMPT = "Поясни різницю між функцією і методом. Коротко."

MODELS = ["llama3.2:3b", "qwen3:4b"]

SYSTEMS = [
    "Ти лаконічний технічний асистент.",
    "Відповідай лише українською, максимум двома реченнями."
]

results = []

def ask_model(model, system_message):
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": PROMPT}
        ],
        "stream": False,
        "options": {
            "temperature": 0.7
        }
    }

    request = Request(
        "http://localhost:11434/api/chat",
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    with urlopen(request, timeout=300) as response:
        return json.loads(response.read().decode("utf-8"))


for model in MODELS:
    for system_message in SYSTEMS:
        print(f"\nМодель: {model}")
        print(f"System: {system_message}")
        print("Очікуємо відповідь...")

        start = time.perf_counter()
        response = ask_model(model, system_message)
        duration = time.perf_counter() - start

        answer = response["message"]["content"]

        prompt_tokens = response.get("prompt_eval_count", 0)
        completion_tokens = response.get("eval_count", 0)

        result = {
            "model": model,
            "system": system_message,
            "answer": answer,
            "length": len(answer),
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "time_seconds": round(duration, 2)
        }

        results.append(result)

        print("Відповідь:", answer)
        print("Довжина:", len(answer), "символів")
        print("Prompt tokens:", prompt_tokens)
        print("Completion tokens:", completion_tokens)
        print(f"Час: {duration:.2f} с")


with open("system_results.json", "w", encoding="utf-8") as file:
    json.dump(results, file, ensure_ascii=False, indent=4)

print("\nТестування завершено!")
print("Результати збережено у system_results.json")