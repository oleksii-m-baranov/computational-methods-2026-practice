import time

from providers import make_client

client, model = make_client("local")
prompt = "Столиця Бразилії?"  # Короткий промпт

print("Надсилаю запит до локальної моделі...")
t_start = time.perf_counter()
first_token_at = None

stream = client.chat.completions.create(
    model=model,
    messages=[{"role": "user", "content": prompt}],
    stream=True,
)

for chunk in stream:
    if chunk.choices[0].delta.content and first_token_at is None:
        first_token_at = time.perf_counter()

t_end = time.perf_counter()

print(f"TTFT, с: {first_token_at - t_start:.3f}")
print(f"Всього, с: {t_end - t_start:.3f}")
