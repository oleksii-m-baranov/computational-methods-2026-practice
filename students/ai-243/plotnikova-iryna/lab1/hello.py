from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",   # адреса локальної Ollama
    api_key="ollama",
)

SYSTEM_1 = "Ти лаконічний технічний асистент."
SYSTEM_2 = "Відповідай лише українською, максимум двома реченнями."
USER = "Поясни різницю між процесом і потоком."

for sys_prompt in [SYSTEM_1, SYSTEM_2]:
    print(f"\n--- SYSTEM: {sys_prompt} ---")
    response = client.chat.completions.create(
        model="qwen3:4b", 
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user",   "content": USER},
        ],
        temperature=0.7,
    )
    print(response.choices[0].message.content)
    print("\nВитрати токенів:", response.usage)
