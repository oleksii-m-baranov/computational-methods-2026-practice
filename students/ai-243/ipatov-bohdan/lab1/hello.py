import json
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)

USER_PROMPT = "Поясни різницю між списком і кортежем у Python."

SYSTEM_PROMPTS = [
    ("concise", "Ти лаконічний технічний асистент."),
    ("ukrainian_2_sentences", "Відповідай лише українською, максимум двома реченнями."),
]

MODELS = ["llama3.2:3b", "qwen3:4b"]

results = []

for model in MODELS:
    for sys_label, sys_prompt in SYSTEM_PROMPTS:
        print(f"=== Model: {model} | System: {sys_label} ===")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": USER_PROMPT},
            ],
            temperature=0.7,
        )
        content = response.choices[0].message.content or ""
        usage = response.usage

        # Count sentences roughly by period/exclamation/question
        sentences = [s.strip() for s in content.replace("\n", " ").split(".") if s.strip()]
        sentence_count = len(sentences)

        record = {
            "model": model,
            "system_label": sys_label,
            "system_prompt": sys_prompt,
            "content": content,
            "char_len": len(content),
            "sentence_count": sentence_count,
            "prompt_tokens": usage.prompt_tokens if usage else 0,
            "completion_tokens": usage.completion_tokens if usage else 0,
            "total_tokens": usage.total_tokens if usage else 0,
        }
        results.append(record)
        print(f"Length: {len(content)} chars, Sentences: ~{sentence_count}")
        print("Usage:", usage)
        print(content)
        print()

with open("hello_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("Saved hello_results.json")
