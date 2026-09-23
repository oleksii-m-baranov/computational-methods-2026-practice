import time
from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
prompt = "Столиця Бразилії?"

t_start = time.perf_counter()
first_token_at = None

stream = client.chat.completions.create(
    model="llama3.2:3b",
    messages=[{"role": "user", "content": prompt}],
    stream=True,
)

for chunk in stream:
    piece = chunk.choices[0].delta.content
    if piece:
        if first_token_at is None:
            first_token_at = time.perf_counter()

t_end = time.perf_counter()

print(f"TTFT, c: {first_token_at - t_start:.3f}")
print(f"Всього, c: {t_end - t_start:.3f}")