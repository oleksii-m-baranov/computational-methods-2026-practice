import argparse
import csv
import os
import shutil
import statistics
import subprocess
import time
from providers import make_client
from utils.lab_logger import custom_logger


def measure(client, model: str, prompt: str) -> dict:
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
                first_token_at = time.perf_counter()
            parts.append(piece)

    t_end = time.perf_counter()
    text = "".join(parts)
    ttft = (first_token_at - t_start) if first_token_at is not None else (t_end - t_start)
    total = t_end - t_start

    return {
        "ttft_s": round(ttft, 3),
        "total_s": round(total, 3),
        "chars": len(text),
        "chars_per_s": round(len(text) / total, 1) if total > 0 else 0.0,
    }


PROMPTS = {
    "short": "Столиця Індії?",
    "medium": "Поясни в одному абзаці, що таке рекурсія.",
    "long": "Напиши інструкцію з 10 пунктів, як спроєктувати просту базу даних.",
}


def run_benchmark():
    logger = custom_logger("task4_benchmark", overwrite=True)
    rows = []

    for provider in ["local", "cloud"]:
        client, model = make_client(provider)
        warmup = measure(client, model, "розігрів")
        logger.info(f"Warmup [{provider} | {model}]: {warmup}")

        for name, prompt in PROMPTS.items():
            runs = []
            for i in range(1, 4):
                r = measure(client, model, prompt)
                runs.append(r)
                logger.info(f"  run {i}/3 [{provider} | {name}]: {r}")
            row = {
                "provider": provider,
                "model": model,
                "prompt": name,
                "ttft_s": round(statistics.median(r["ttft_s"] for r in runs), 3),
                "total_s": round(statistics.median(r["total_s"] for r in runs), 3),
                "chars_per_s": round(statistics.median(r["chars_per_s"] for r in runs), 1),
            }
            rows.append(row)
            logger.info(f"MEDIAN: {row}")

    with open("results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    logger.info("Saved results.csv")


def run_cold_warm():
    logger = custom_logger("task4_cold_warm", overwrite=True)
    client, model = make_client("local")
    ollama_bin = shutil.which("ollama") or os.path.expandvars(r"%LOCALAPPDATA%\Programs\Ollama\ollama.exe")
    subprocess.run([ollama_bin, "stop", model], check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(1.5)
    cold = measure(client, model, PROMPTS["short"])
    logger.info(f"COLD START [{model} | short]: {cold}")
    warm = measure(client, model, PROMPTS["short"])
    logger.info(f"WARM START [{model} | short]: {warm}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cold-warm", action="store_true", help="Вимір холодного і теплого старту")
    args = parser.parse_args()
    if args.cold_warm:
        run_cold_warm()
    else:
        run_benchmark()
