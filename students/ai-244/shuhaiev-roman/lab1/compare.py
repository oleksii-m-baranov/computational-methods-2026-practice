"""Завдання 3. Локальна vs хмарна модель: єдиний інтерфейс."""
import time
from providers import make_client, sampling_params, get_logger, save_json

log = get_logger()

QUESTION = "Поясни різницю між оперативною пам'яттю і жорстким диском. Коротко."

results = []
for name in ["local", "cloud"]:
    client, model = make_client(name)

    t0 = time.perf_counter()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": QUESTION}],
        **sampling_params(name, temperature=0.7),
    )
    elapsed = time.perf_counter() - t0
    text = response.choices[0].message.content

    print(f"===== {name.upper()} ({model}) =====")
    print(text)
    print(f"Час: {elapsed:.2f} с")
    print(response.usage)
    print()

    results.append({
        "provider": name,
        "model": model,
        "time_s": round(elapsed, 2),
        "completion_tokens": response.usage.completion_tokens,
        "chars": len(text),
        "answer": text,
    })
    log.info(f"[compare] {name} {model}: time={elapsed:.2f}s chars={len(text)}")

print("Збережено:", save_json("task3_compare.json", results))
