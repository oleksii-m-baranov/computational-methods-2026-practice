"""Завдання 2: вплив system-повідомлення (варіант 7)."""
import json
from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

SYSTEMS = {
    "laconic": "Ти лаконічний технічний асистент.",
    "ukr2": "Відповідай лише українською, максимум двома реченнями.",
}
USER = "Поясни різницю між процесом і потоком."

rows = []
for model in ["llama3.2:3b", "qwen3:4b"]:
    for key, system in SYSTEMS.items():
        r = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": USER}],
            temperature=0.7,
        )
        text = r.choices[0].message.content
        row = {
            "model": model,
            "system": key,
            "chars": len(text),
            "prompt_tokens": r.usage.prompt_tokens,
            "completion_tokens": r.usage.completion_tokens,
            "total_tokens": r.usage.total_tokens,
            "text": text,
        }
        rows.append(row)
        print(f"===== {model} / {key} =====")
        print(text)
        print({k: v for k, v in row.items() if k != "text"})
        print()

with open("hello_results.json", "w", encoding="utf-8") as f:
    json.dump(rows, f, ensure_ascii=False, indent=2)
