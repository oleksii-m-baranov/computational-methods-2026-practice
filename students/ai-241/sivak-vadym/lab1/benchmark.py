"""Завдання 4. Вимірювання швидкості: TTFT і залежність від довжини запиту (варіант 7)."""
import time
import statistics
import csv

from providers import make_client
from utils.lab_logger import custom_logger

logger = custom_logger('lab1')


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
        if not chunk.choices:
            continue
        piece = chunk.choices[0].delta.content
        if piece:
            if first_token_at is None:
                first_token_at = time.perf_counter()  # зафіксували перший токен
            parts.append(piece)

    t_end = time.perf_counter()
    text = "".join(parts)

    return {
        "ttft_s": round(first_token_at - t_start, 3),
        "total_s": round(t_end - t_start, 3),
        "chars": len(text),
        "chars_per_s": round(len(text) / (t_end - t_start), 1),
    }


# пауза між хмарними вимірами: безкоштовний Groq дає 8000 токенів/хв,
# а повтор після 429 потрапив би всередину виміру й спотворив час
CLOUD_PAUSE_S = 20

PROMPTS = {
    "short": "Столиця Норвегії?",
    "medium": "Поясни в одному абзаці, що таке рекурсія.",
    "long": "Напиши інструкцію з 10 пунктів, як провести код-рев'ю.",
}

if __name__ == "__main__":
    logger.info("===== BENCHMARK =====")
    rows = []
    for provider in ["local", "cloud"]:
        client, model = make_client(provider)

        measure(client, model, "розігрів")  # прогрів, не рахуємо

        for name, prompt in PROMPTS.items():
            runs = []
            for _ in range(3):
                if provider == "cloud":
                    time.sleep(CLOUD_PAUSE_S)  # поза вимірюванням: не впертися в ліміт токенів/хв
                runs.append(measure(client, model, prompt))
            logger.info(f"{provider} | {name} | 3 повтори: {runs}")
            rows.append({
                "provider": provider,
                "model": model,
                "prompt": name,
                "ttft_s": statistics.median(r["ttft_s"] for r in runs),
                "total_s": statistics.median(r["total_s"] for r in runs),
                "chars_per_s": statistics.median(r["chars_per_s"] for r in runs),
            })
            logger.info(rows[-1])

    with open("results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    logger.info("Результати збережено в results.csv")
