from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",  # адреса локальної Ollama
    api_key="ollama",                      # Ollama ключ не перевіряє, але поле обов'язкове
)

SYSTEM_PROMPTS = [
    "Ти лаконічний технічний асистент.",
    "Відповідай лише українською, максимум двома реченнями."
]
USER_PROMPT = "Поясни різницю між реляційною і документоорієнтованою базою даних."

for model in ["llama3.2:3b", "qwen3:4b"]:
    for sys_msg in SYSTEM_PROMPTS:
        print(f"=== Модель: {model} | System: {sys_msg} ===")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": sys_msg},
                {"role": "user", "content": USER_PROMPT},
            ],
            temperature=0.7,
        )
        content = response.choices[0].message.content
        print(content)
        print(f"Довжина символів: {len(content)}")
        print(response.usage)
        print()
