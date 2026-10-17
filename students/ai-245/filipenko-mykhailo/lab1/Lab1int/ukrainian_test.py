import json
from urllib.request import Request, urlopen

models = ["llama3.2:3b", "qwen3:4b"]

question = """
Виправ помилки в реченні та коротко поясни їх:

"На протязі неділі я приймав участь
у міроприємствах по програмуванню."

Відповідай українською мовою.
"""

results = []

for model in models:
    print(f"\nТестуємо модель: {model}")
    print("Очікуємо відповідь...")

    data = {
        "model": model,
        "prompt": question,
        "stream": False,
        "options": {"temperature": 0.3}
    }

    request = Request(
        "http://localhost:11434/api/generate",
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    with urlopen(request, timeout=300) as response:
        result = json.loads(response.read().decode("utf-8"))

    answer = result["response"]
    print("Відповідь:", answer)

    results.append({
        "model": model,
        "question": question.strip(),
        "answer": answer
    })

with open("ukrainian_results.json", "w", encoding="utf-8") as file:
    json.dump(results, file, ensure_ascii=False, indent=4)

print("\nГотово! Результати збережено у ukrainian_results.json")