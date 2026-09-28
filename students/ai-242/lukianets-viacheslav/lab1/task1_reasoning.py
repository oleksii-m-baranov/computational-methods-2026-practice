"""Завдання 1: ціна роздумів. Прямий запит до Ollama /api/generate, тривалості в наносекундах."""
import json
import statistics
import urllib.request
from utils.lab_logger import custom_logger

logger = custom_logger("lab1")

URL = "http://localhost:11434/api/generate"
MODELS = ["qwen3:4b", "llama3.2:3b"]
FACT = "Столиця України? Відповідай одним словом."
PUZZLE = ("Ручка і зошит разом коштують 110 грн. Ручка на 100 грн дешевша за зошит. "
          "Скільки коштує ручка?")


def generate(model, prompt):
    body = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode("utf-8")
    req = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=900) as resp:
        return json.loads(resp.read().decode("utf-8"))


def stats(d):
    return {
        "response": d["response"].strip(),
        "done_reason": d.get("done_reason"),
        "eval_count": d["eval_count"],
        "time_s": round(d["total_duration"] / 1e9, 2),
        "tok_per_s": round(d["eval_count"] / (d["eval_duration"] / 1e9), 1),
        "thinking_chars": len(d.get("thinking") or ""),
    }


for model in MODELS:
    generate(model, "розігрів")  # прогрів, щоб load_duration не спотворював час
    logger.info(f"TABLE1 {model}: {stats(generate(model, FACT))}")

for model in MODELS:
    runs = [generate(model, PUZZLE) for _ in range(5)]
    for i, d in enumerate(runs, 1):
        logger.info(f"TABLE2 {model} run {i}: {stats(d)}")
    logger.info(
        f"TABLE2 {model} AVG: eval_count={statistics.mean(d['eval_count'] for d in runs):.0f}, "
        f"time_s={statistics.mean(d['total_duration'] for d in runs) / 1e9:.2f}"
    )
