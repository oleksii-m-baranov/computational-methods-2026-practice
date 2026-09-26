from openai import OpenAI


client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)

SYSTEM = "Відповідай лише українською, максимум двома реченнями."
USER = "Поясни різницю між функцією і методом."

response = client.chat.completions.create(
    model="qwen3:4b",
    messages=[
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": USER},
    ],
    temperature=0.7,
)

content = response.choices[0].message.content
print(content)
print(response.usage)

