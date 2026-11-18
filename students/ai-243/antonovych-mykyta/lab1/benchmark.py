import csv
import statistics
import subprocess
import time
from pathlib import Path

import matplotlib.pyplot as plt
from openai import RateLimitError

from providers import make_client
from utils.lab_logger import custom_logger


logger = custom_logger("lab1")

LAB_DIR = Path(__file__).resolve().parent


PROMPTS = {
    "short": "Столиця Японії?",
    "medium": "Поясни в одному абзаці, що таке рекурсія.",
    "long": (
        "Напиши інструкцію з 10 пунктів, "
        "як налаштувати робоче середовище розробника."
    ),
}


def measure(client, model, prompt):
    """
    Один вимір:
    повертає TTFT, загальний час,
    кількість символів та символів/с.
    """

    while True:
        try:
            t_start = time.perf_counter()

            first_token_at = None
            parts = []

            stream = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                stream=True,
            )

            for chunk in stream:
                piece = chunk.choices[0].delta.content

                if piece:
                    if first_token_at is None:
                        first_token_at = time.perf_counter()

                    parts.append(piece)

            t_end = time.perf_counter()

            text = "".join(parts)

            if first_token_at is None:
                first_token_at = t_end

            return {
                "ttft_s": round(
                    first_token_at - t_start,
                    3,
                ),
                "total_s": round(
                    t_end - t_start,
                    3,
                ),
                "chars": len(text),
                "chars_per_s": round(
                    len(text) / (t_end - t_start),
                    1,
                ),
            }

        except RateLimitError:
            logger.info(
                "Rate limit 429. Чекаємо 65 секунд..."
            )

            time.sleep(65)


def run_main_benchmark():
    rows = []

    for provider in ["local", "cloud"]:
        client, model = make_client(provider)

        logger.info(
            f"===== PROVIDER: {provider} / {model} ====="
        )

        # Прогрів.
        # Для cloud робимо паузу,
        # щоб не вилетіти за free-tier rate limit.
        if provider == "cloud":
            time.sleep(15)

        logger.info(
            f"{provider} / warm-up"
        )

        measure(
            client,
            model,
            "розігрів",
        )

        for prompt_name, prompt in PROMPTS.items():
            runs = []

            for run_number in range(1, 4):

                if provider == "cloud":
                    time.sleep(15)

                result = measure(
                    client,
                    model,
                    prompt,
                )

                runs.append(result)

                logger.info(
                    f"{provider} / "
                    f"{model} / "
                    f"{prompt_name} / "
                    f"run {run_number}: "
                    f"{result}"
                )

            row = {
                "provider": provider,
                "model": model,
                "prompt": prompt_name,
                "ttft_s": statistics.median(
                    r["ttft_s"]
                    for r in runs
                ),
                "total_s": statistics.median(
                    r["total_s"]
                    for r in runs
                ),
                "chars_per_s": statistics.median(
                    r["chars_per_s"]
                    for r in runs
                ),
            }

            rows.append(row)

            logger.info(
                f"MEDIAN: {row}"
            )

    csv_path = LAB_DIR / "results.csv"

    with open(
        csv_path,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "provider",
                "model",
                "prompt",
                "ttft_s",
                "total_s",
                "chars_per_s",
            ],
        )

        writer.writeheader()
        writer.writerows(rows)

    logger.info(
        f"Results saved: {csv_path}"
    )

    return rows


def make_chart(rows):
    labels = [
        f"{row['provider']}\n{row['prompt']}"
        for row in rows
    ]

    values = [
        row["chars_per_s"]
        for row in rows
    ]

    plt.figure(
        figsize=(10, 6)
    )

    plt.bar(
        labels,
        values,
    )

    plt.xlabel(
        "Модель × промпт"
    )

    plt.ylabel(
        "Символів за секунду"
    )

    plt.title(
        "Швидкість генерації відповідей"
    )

    plt.tight_layout()

    chart_path = (
        LAB_DIR / "benchmark.png"
    )

    plt.savefig(
        chart_path,
        dpi=200,
    )

    plt.close()

    logger.info(
        f"Chart saved: {chart_path}"
    )


def cold_warm_test():
    logger.info(
        "===== COLD / WARM TEST ====="
    )

    client, model = make_client(
        "local"
    )

    # Повністю вивантажуємо модель
    # з пам'яті Ollama.
    subprocess.run(
        [
            "ollama",
            "stop",
            model,
        ],
        check=False,
    )

    time.sleep(2)

    # Перший запит після stop = cold.
    cold = measure(
        client,
        model,
        PROMPTS["short"],
    )

    logger.info(
        f"COLD: {cold}"
    )

    # Наступний запит = warm.
    warm = measure(
        client,
        model,
        PROMPTS["short"],
    )

    logger.info(
        f"WARM: {warm}"
    )


if __name__ == "__main__":
    logger.info(
        "===== TASK 4 ====="
    )

    rows = run_main_benchmark()

    make_chart(rows)

    cold_warm_test()

    logger.info(
        "===== TASK 4 FINISHED ====="
    )
