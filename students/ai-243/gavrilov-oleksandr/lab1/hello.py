from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama", # Ollama не перевіряє ключ, але бібліотека його вимагає
)

# === ЗМІНЮЙ ЦІ ДАНІ ДЛЯ РІЗНИХ ЗАПУСКІВ ===
CURRENT_MODEL = "qwen3:4b" 
SYSTEM = "Відповідай лише українською, максимум двома реченнями." 
USER = "Поясни різницю між оперативною пам’яттю і жорстким диском."
# ==========================================

response = client.chat.completions.create(
    model=CURRENT_MODEL,
    messages=[
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": USER},
    ],
    temperature=0.7,
)

print("\n--- ВІДПОВІДЬ МОДЕЛІ ---")
print(response.choices[0].message.content)
print("\n--- СТАТИСТИКА ТОКЕНІВ (для Таблиці 4) ---")
print(response.usage)
