
"""ЛР №1: три прогони з медіаною для однієї обраної моделі."""

import argparse
import csv
import statistics
import time
from pathlib import Path
from providers import make_client

FILE = Path(__file__).with_name("results.csv")

FIELDS = [
    "provider", "model", "prompt",
    "ttft_s", "total_s", "chars_per_s"
]

PROMPTS = {
    "short": "Столиця Японії?",
    "medium": "Поясни в одному абзаці, що таке рекурсія.",
    "long": (
        "Напиши інструкцію з 10 пунктів, "
        "як налаштувати робоче середовище розробника."
    ),
}

MODELS = {
    "llama": "llama3.2:3b",
    "qwen": "qwen3:4b",
    "cloud": "gemini-3.5-flash-lite",
}


def measure(client, model, prompt):
    start = time.perf_counter()
    first = None
    chunks = []

    stream = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ],
        stream=True,
    )

    for part in stream:
        if not part.choices:
            continue

        value = part.choices[0].delta.content

        if value:
            if first is None:
                first = time.perf_counter()
            chunks.append(value)

    total = time.perf_counter() - start
    text = "".join(chunks)

    if not text:
        raise ValueError(
            "Не отримано текстової відповіді"
        )

    return {
        "ttft_s": first - start,
        "total_s": total,
        "chars_per_s": len(text) / total,
    }


def save_row(row):
    old = []

    if FILE.exists():
        with FILE.open(
            "r", encoding="utf-8", newline=""
        ) as f:
            old = list(csv.DictReader(f))

    old = [
        r for r in old
        if not (
            r.get("model") == row["model"]
            and r.get("prompt") == row["prompt"]
        )
    ]

    old.append(row)

    with FILE.open(
        "w", encoding="utf-8", newline=""
    ) as f:
        writer = csv.DictWriter(
            f, fieldnames=FIELDS
        )
        writer.writeheader()
        writer.writerows(old)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--model",
        required=True,
        choices=MODELS
    )
    parser.add_argument(
        "--dry-run",
        action="store_true"
    )

    args = parser.parse_args()
    name = MODELS[args.model]

    print(
        f"Модель: {name}; "
        "1 прогрів + 3 повтори × 3 промпти"
    )

    if args.dry_run:
        print(
            "DRY RUN OK: запитів немає; "
            "results.csv не змінено"
        )
        return

    provider = (
        "cloud" if args.model == "cloud"
        else "local"
    )

    client, _ = make_client(provider)

    try:
        measure(
            client,
            name,
            "Тестовий запит для прогріву."
        )

        for short, prompt in PROMPTS.items():
            samples = [
                measure(client, name, prompt)
                for _ in range(3)
            ]

            row = {
                "provider": provider,
                "model": name,
                "prompt": short
            }

            for metric in (
                "ttft_s",
                "total_s",
                "chars_per_s"
            ):
                row[metric] = round(
                    statistics.median(
                        x[metric] for x in samples
                    ),
                    3
                )

            save_row(row)

            print(
                f"{short}: "
                f"TTFT={row['ttft_s']} с, "
                f"загалом={row['total_s']} с, "
                f"симв/с={row['chars_per_s']}"
            )

        if args.model == "cloud":
            with FILE.open(
                "r", encoding="utf-8", newline=""
            ) as f:
                rows = list(csv.DictReader(f))

            rows = [
                r for r in rows
                if r.get("model") != "gemini-3.8-flash"
            ]

            with FILE.open(
                "w", encoding="utf-8", newline=""
            ) as f:
                writer = csv.DictWriter(
                    f, fieldnames=FIELDS
                )
                writer.writeheader()
                writer.writerows(rows)

            print(
                "Старі неповні виміри Gemini 3.8 "
                "вилучено з results.csv"
            )

    except KeyboardInterrupt:
        print(
            "\nЗупинено. Уже записані рядки збережені"
        )

    except Exception as exc:
        status = getattr(
            exc, "status_code", None
        )

        if (
            status == 429
            or "RESOURCE_EXHAUSTED" in str(exc)
        ):
            print(
                "Помилка 429: ліміт Google. "
                "Недостовірних чисел не записуємо"
            )
        else:
            print(
                f"Помилка вимірювання: "
                f"{type(exc).__name__} (HTTP {status})"
            )

        print(
            "Повтори запуск після усунення проблеми"
        )


if __name__ == "__main__":
    main()
