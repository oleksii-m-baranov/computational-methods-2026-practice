import json

with open("quality.json", "r", encoding="utf-8") as f:
    data = json.load(f)

models = [
    "llama3.2:3b",
    "qwen3:4b",
    "gemini-3.8-flash"
]

for model in models:
    print(f"\n=== {model} ===")

    for i, answer in enumerate(data[model]["2_format"], start=1):

        try:
            parsed = json.loads(answer)
            print(f"Запуск {i}: JSON коректний")
            print(parsed)

        except Exception as e:
            print(f"Запуск {i}: НЕ парситься")
            print(f"Причина: {e}")