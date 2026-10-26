import csv
import statistics
import time
from providers import make_client


def measure(client, model, prompt):
    """Один вимір: повертає TTFT, загальний час і довжину відповіді."""
    t_start = time.perf_counter()
    first_token_at = None
    parts = []

    stream = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )

    for chunk in stream:
        piece = chunk.choices[0].delta.content
        if piece:
            if first_token_at is None:
                first_token_at = time.perf_counter()  # зафіксували перший токен
            parts.append(piece)

    # Виносимо t_end і return ЗА МЕЖІ циклу for, коли весь текст уже отримано!
    t_end = time.perf_counter()
    text = "".join(parts)

    # Захист від ділення на нуль, якщо текст чомусь пустий
    duration = t_end - t_start
    if duration == 0:
        duration = 0.001

    return {
        "ttft_s": round(
            first_token_at - t_start if first_token_at else duration, 3
        ),
        "total_s": round(duration, 3),
        "chars": len(text),
        "chars_per_s": round(len(text) / duration, 1),
    }


PROMPTS = {
    "short": "Столиця Норвегії?",
    "medium": "Поясни в одному абзаці, що таке рекурсія.",
    "long": "Напиши інструкцію з 10 пунктів, як провести кодрев’ю",
}

rows = []
for provider in ["local", "cloud"]:
    client, model = make_client(provider)

    print(f"Провідник: {provider} ({model})")
    measure(client, model, "розігрів")  # прогрів, не рахуємо
    time.sleep(5)  # пауза після розігріву

    for name, prompt in PROMPTS.items():
        print(f"  -> Тестуємо промпт: {name}")
        runs = []
        for _ in range(3):
            runs.append(measure(client, model, prompt))
            time.sleep(
                12
            )  # Пауза 12 секунд між запусками, щоб не зловити ліміт 429

        rows.append(
            {
                "provider": provider,
                "model": model,
                "prompt": name,
                "ttft_s": statistics.median(r["ttft_s"] for r in runs),
                "total_s": statistics.median(r["total_s"] for r in runs),
                "chars_per_s": statistics.median(
                    r["chars_per_s"] for r in runs
                ),
            }
        )
        print(rows[-1])

with open("results.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print("Бенчмарк успішно завершено! Результати у файлі results.csv")