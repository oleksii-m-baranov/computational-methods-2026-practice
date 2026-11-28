import json
import urllib.request
from utils.lab_logger import custom_logger

logger = custom_logger("task1_thinking", overwrite=True)

OLLAMA_URL = "http://localhost:11434/api/generate"


def generate_raw(model: str, prompt: str) -> dict:
    """Надсилає прямий POST-запит до Ollama /api/generate без стрімінгу."""
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=900) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fmt_metrics(data: dict) -> dict:
    total_s = data.get("total_duration", 0) / 1e9
    eval_s = data.get("eval_duration", 0) / 1e9
    eval_cnt = data.get("eval_count", 0)
    tok_s = eval_cnt / eval_s if eval_s > 0 else 0.0
    return {
        "response": (data.get("response") or "").strip(),
        "thinking_len": len(data.get("thinking") or ""),
        "done_reason": data.get("done_reason"),
        "prompt_eval_count": data.get("prompt_eval_count", 0),
        "prompt_eval_cached_count": data.get("prompt_eval_cached_count", 0),
        "eval_count": eval_cnt,
        "total_s": round(total_s, 3),
        "tok_s": round(tok_s, 2),
    }


# Крок 2. Ознайомчий запит
logger.info("=== Крок 2: ознайомчий запит до /api/generate ===")
demo = generate_raw("qwen3:4b", "Столиця України?")
logger.info(f"Demo qwen3:4b metrics: {fmt_metrics(demo)}")
logger.info(f"Demo thinking preview (first 400 chars): {(demo.get('thinking') or '')[:400]}")

# Прогрів llama3.2:3b перед вимірюванням
generate_raw("llama3.2:3b", "Привіт")

FACT_PROMPT = "Столиця України? Відповідай одним словом."
REASON_PROMPT = (
    "Ручка і зошит разом коштують 110 грн. "
    "Ручка на 100 грн дешевша за зошит. Скільки коштує ручка?"
)

logger.info("=== Завдання 1, Крок 1: Просте фактичне питання ===")
for model in ["qwen3:4b", "llama3.2:3b"]:
    res = fmt_metrics(generate_raw(model, FACT_PROMPT))
    logger.info(f"[{model}] {res}")

logger.info("=== Завдання 1, Крок 2: Задача на міркування (по 5 запусків) ===")
for model in ["qwen3:4b", "llama3.2:3b"]:
    eval_counts = []
    times = []
    for i in range(1, 6):
        res = fmt_metrics(generate_raw(model, REASON_PROMPT))
        eval_counts.append(res["eval_count"])
        times.append(res["total_s"])
        logger.info(
            f"[{model}] run {i}/5: eval_count={res['eval_count']}, "
            f"total_s={res['total_s']}, tok_s={res['tok_s']} | response={res['response']!r}"
        )
    logger.info(
        f"[{model}] AVERAGE: eval_count={round(sum(eval_counts)/5, 1)}, "
        f"total_s={round(sum(times)/5, 3)}"
    )
