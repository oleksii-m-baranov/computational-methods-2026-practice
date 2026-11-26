
import json
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

MODELS = ["llama3.2:3b", "qwen3:4b"]

SYSTEMS = [
    "Ти лаконічний технічний асистент.",
    "Відповідай лише українською, максимум двома реченнями."
]

USER = "Поясни різницю між стеком і чергою."

results = []

for model in MODELS:
    for system in SYSTEMS:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": USER}
            ],
            temperature=0.7
        )

        text = response.choices[0].message.content or ""

        result = {
            "model": model,
            "system": system,
            "response": text,
            "chars": len(text),
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
            "finish_reason": response.choices[0].finish_reason
        }

        results.append(result)

        print(json.dumps(
            result, ensure_ascii=False, indent=2
        ))

with open("task2_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("Результати збережено у task2_results.json")
