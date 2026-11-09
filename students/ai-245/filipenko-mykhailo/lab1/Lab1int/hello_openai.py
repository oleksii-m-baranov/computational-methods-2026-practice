from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

SYSTEM = "Ти лаконічний технічний асистент."
USER = "Поясни різницю між функцією і методом у програмуванні Python. Наведи короткий приклад."

response = client.chat.completions.create(
model="qwen3:4b",
    messages=[
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": USER}
    ],
    temperature=0.7
)

print(response.choices[0].message.content)
print(response.usage)
