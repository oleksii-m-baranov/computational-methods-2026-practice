import csv
import time
from providers import make_client

QUESTION = "Поясни різницю між функцією і методом. Коротко."

results = []

for provider in ["llama", "cloud"]:
    client, model = make_client(provider)

    start = time.perf_counter()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": QUESTION}
        ],
        temperature=0.7,
    )

    elapsed = round(time.perf_counter() - start, 2)
    answer = response.choices[0].message.content or ""
    usage = response.usage

    result = {
        "provider": provider,
        "model": model,
        "seconds": elapsed,
        "completion_tokens": usage.completion_tokens if usage else 0,
        "chars": len(answer),
        "language": "потребує перевірки",
        "factual_errors": "потребує перевірки",
    }

    results.append(result)

    print(f"\n===== {provider.upper()} ({model}) =====")
    print(answer)
    print(f"Час: {elapsed} с")
    print(f"Токенів відповіді: {result['completion_tokens']}")
    print(f"Символів: {result['chars']}")

with open("compare_results.csv", "w", newline="", encoding="utf-8-sig") as file:
    writer = csv.DictWriter(file, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)

print("\nРезультати збережено у compare_results.csv")

