import json
import statistics
import urllib.request

from utils.lab_logger import custom_logger

logger = custom_logger("lab1")

URL = "http://localhost:11434/api/generate"

MODELS = [
    "qwen3:4b",
    "llama3.2:3b",
]

FACT_PROMPT = "Столиця України? Відповідай одним словом."

REASONING_PROMPT = (
    "Ручка і зошит разом коштують 110 грн. "
    "Ручка на 100 грн дешевша за зошит. "
    "Скільки коштує ручка?"
)


def generate(model, prompt):
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
    }).encode("utf-8")

    request = urllib.request.Request(
        URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


def seconds(ns):
    return ns / 1e9


logger.info("===== TASK 1 =====")

# Прогрів — у таблиці не враховуємо
for model in MODELS:
    logger.info(f"Warm-up: {model}")
    generate(model, "Розігрів")

# Фактичне питання
logger.info("===== FACTUAL QUESTION =====")

for model in MODELS:
    data = generate(model, FACT_PROMPT)

    eval_count = data.get("eval_count", 0)
    eval_duration = data.get("eval_duration", 0)
    total_duration = data.get("total_duration", 0)

    total_s = seconds(total_duration)

    tokens_per_s = (
        eval_count / seconds(eval_duration)
        if eval_duration
        else 0
    )

    logger.info(f"MODEL: {model}")
    logger.info(f"response: {data.get('response')}")
    logger.info(f"eval_count: {eval_count}")
    logger.info(f"time_s: {total_s:.3f}")
    logger.info(f"tokens_per_s: {tokens_per_s:.3f}")

    thinking = data.get("thinking")
    if thinking:
        logger.info(f"thinking: {thinking}")

# Задача на міркування
logger.info("===== REASONING QUESTION: 5 RUNS =====")

for model in MODELS:
    eval_counts = []
    times = []

    for run in range(1, 6):
        data = generate(model, REASONING_PROMPT)

        eval_count = data.get("eval_count", 0)
        total_s = seconds(data.get("total_duration", 0))

        eval_counts.append(eval_count)
        times.append(total_s)

        logger.info(f"MODEL: {model}, RUN: {run}")
        logger.info(f"response: {data.get('response')}")
        logger.info(f"eval_count: {eval_count}")
        logger.info(f"time_s: {total_s:.3f}")

    logger.info(f"MODEL: {model}")
    logger.info(
        f"average_eval_count: {statistics.mean(eval_counts):.2f}"
    )
    logger.info(
        f"average_time_s: {statistics.mean(times):.3f}"
    )
