"""Завдання 2 (варіант 1): вплив system-повідомлення.

Запускає 2 моделі x 2 system-повідомлення, друкує відповіді та показники
для таблиць і зберігає все у task2_raw.json.
"""
import json
import re

from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",  # адреса локальної Ollama
    api_key="ollama",                      # Ollama ключ не перевіряє, але поле обов'язкове
)

USER = "Поясни різницю між списком і кортежем у Python."

SYSTEMS = {
    "лаконічний асистент": "Ти лаконічний технічний асистент.",
    "українською, 2 речення": "Відповідай лише українською, максимум двома реченнями.",
}

MODELS = ["llama3.2:3b", "qwen3:4b"]


def count_sentences(text):
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return len([p for p in parts if p.strip()])


def language_hint(text):
    """Груба евристика: українські літери (і ї є ґ) проти російських (ы э ъ ё)."""
    low = text.lower()
    ukr = sum(low.count(c) for c in "іїєґ")
    rus = sum(low.count(c) for c in "ыэъё")
    latin = len(re.findall(r"[a-z]{4,}", low))
    return ukr, rus, latin


results = []

for model in MODELS:
    for label, system in SYSTEMS.items():
        print(f"\n>>> {model} | {label} ... (зачекайте)")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": USER},
            ],
            temperature=0.7,
        )
        text = response.choices[0].message.content.strip()
        u = response.usage
        ukr, rus, latin = language_hint(text)
        row = {
            "model": model,
            "system": label,
            "chars": len(text),
            "sentences": count_sentences(text),
            "ukr_letters": ukr,
            "rus_letters": rus,
            "latin_words": latin,
            "prompt_tokens": u.prompt_tokens,
            "completion_tokens": u.completion_tokens,
            "total_tokens": u.total_tokens,
            "text": text,
        }
        results.append(row)

        print("-" * 60)
        print(text)
        print("-" * 60)
        print(f"символів={row['chars']}, речень≈{row['sentences']}, "
              f"укр.літер={ukr}, рос.літер={rus}, англ.слів={latin}")
        print(f"prompt={u.prompt_tokens}, completion={u.completion_tokens}, total={u.total_tokens}")

with open("task2_raw.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\n\n===== ПІДСУМОК ДЛЯ ТАБЛИЦЬ =====")
print(f"{'Модель':<13}{'System':<25}{'симв':>6}{'реч':>5}{'укр':>5}{'рос':>5}"
      f"{'prompt':>8}{'compl':>7}{'total':>7}")
for r in results:
    print(f"{r['model']:<13}{r['system']:<25}{r['chars']:>6}{r['sentences']:>5}"
          f"{r['ukr_letters']:>5}{r['rus_letters']:>5}"
          f"{r['prompt_tokens']:>8}{r['completion_tokens']:>7}{r['total_tokens']:>7}")
print("\nВідповіді збережено у task2_raw.json")
