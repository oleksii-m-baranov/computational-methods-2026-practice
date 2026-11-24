"""Завдання 2. Роль system-повідомлення."""
import re
from openai import OpenAI

from providers import get_logger, save_json

log = get_logger()

client = OpenAI(
    base_url="http://localhost:11434/v1",   # адреса локальної Ollama
    api_key="ollama",                        # Ollama ключ не перевіряє,
                                             # але поле обов'язкове
)

USER = "Поясни різницю між оперативною пам'яттю і жорстким диском."

SYSTEMS = {
    "лаконічний асистент": "Ти лаконічний технічний асистент.",
    "українською, 2 речення": "Відповідай лише українською, максимум двома реченнями.",
}

MODELS = ["llama3.2:3b", "qwen3:4b"]


def count_sentences(text):
    parts = [p for p in re.split(r"(?<=[.!?])\s+", text.strip()) if p.strip()]
    return len(parts)


results = []
for model in MODELS:
    for label, system in SYSTEMS.items():
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": USER},
            ],
            temperature=0.7,
        )
        text = response.choices[0].message.content
        usage = response.usage
        row = {
            "model": model,
            "system": label,
            "answer": text,
            "chars": len(text),
            "sentences_auto": count_sentences(text),
            "prompt_tokens": usage.prompt_tokens,
            "completion_tokens": usage.completion_tokens,
            "total_tokens": usage.total_tokens,
        }
        results.append(row)
        print(f"===== {model} | {label} =====")
        print(text)
        print(usage)
        print()
        log.info(f"[system] {model} | {label}: chars={row['chars']} "
                 f"prompt={row['prompt_tokens']} completion={row['completion_tokens']}")

print("Збережено:", save_json("task2_system.json", results))
