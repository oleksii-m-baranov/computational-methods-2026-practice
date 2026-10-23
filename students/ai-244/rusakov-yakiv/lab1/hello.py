"""Завдання 2. Роль system-повідомлення (варіант 8)."""
import json
import re

from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",   # адреса локальної Ollama
    api_key="ollama",                        # Ollama ключ не перевіряє, але поле обов'язкове
)

USER = "Поясни різницю між реляційною і документоорієнтованою базою даних."

SYSTEMS = {
    "лаконічний асистент": "Ти лаконічний технічний асистент.",
    "українською, 2 речення": "Відповідай лише українською, максимум двома реченнями.",
}
MODELS = ["llama3.2:3b", "qwen3:4b"]

results = []
for model in MODELS:
    for label, system in SYSTEMS.items():
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": USER},
            ],
            temperature=0.7,
        )
        text = response.choices[0].message.content
        usage = response.usage
        sentences = len([s for s in re.split(r"(?<=[.!?…])\s+", text.strip()) if s])
        print(f"===== {model} | {label} =====")
        print(text)
        print(f"символів: {len(text)}, речень (приблизно): {sentences}")
        print(usage)
        print()
        results.append({
            "model": model,
            "system": label,
            "answer": text,
            "chars": len(text),
            "sentences": sentences,
            "prompt_tokens": usage.prompt_tokens,
            "completion_tokens": usage.completion_tokens,
            "total_tokens": usage.total_tokens,
        })

with open("hello_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
