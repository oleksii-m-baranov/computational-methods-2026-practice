from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

USER_PROMPT = "Поясни різницю між стеком і чергою."

SYSTEM_1 = "Ти лаконічний технічний асистент."
SYSTEM_2 = "Відповідай лише українською, максимум двома реченнями."

def run_test(model, system):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": USER_PROMPT}
        ],
        temperature=0.7
    )
    print(f"=== Model: {model} | System: {system} ===")
    print("Content:", response.choices[0].message.content)
    print("Usage:", response.usage)
    print()

run_test("llama3.2:3b", SYSTEM_1)
run_test("llama3.2:3b", SYSTEM_2)
run_test("qwen3:4b", SYSTEM_1)
run_test("qwen3:4b", SYSTEM_2)