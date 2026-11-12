"""Крок 2 і Завдання 1: запити напряму до /api/generate (аналог curl із методички)."""
import json
import statistics
import urllib.request

from utils.lab_logger import custom_logger

logger = custom_logger('lab1')

URL = "http://localhost:11434/api/generate"
MODELS = ["qwen3:4b", "llama3.2:3b"]

FACT = "Столиця України? Відповідай одним словом."
LOGIC = "Ручка і зошит разом коштують 110 грн. Ручка на 100 грн дешевша за зошит. Скільки коштує ручка?"


def generate(model, prompt):
    """Той самий запит, що й curl -d '{"model":..., "prompt":..., "stream":false}'."""
    body = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode("utf-8")
    req = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def metrics(d):
    """час, с = total_duration / 1e9; токенів/с = eval_count / (eval_duration / 1e9)."""
    return {
        "eval_count": d["eval_count"],
        "time_s": round(d["total_duration"] / 1e9, 2),
        "tok_per_s": round(d["eval_count"] / (d["eval_duration"] / 1e9), 2),
    }


def log_response(d):
    logger.info(f"response: {d['response']!r}")
    if d.get("thinking"):
        logger.info(f"thinking ({len(d['thinking'])} симв.): {d['thinking']}")
    for key in ("done", "done_reason", "load_duration", "prompt_eval_count", "prompt_eval_cached_count",
                "prompt_eval_duration", "eval_count", "eval_duration", "total_duration"):
        logger.info(f"  {key}: {d.get(key)}")
    logger.info(f"  context: {len(d.get('context', []))} токенів, перші: {d.get('context', [])[:8]}")
    logger.info(f"  => {metrics(d)}")


# ---- Крок 2: модель – це звичайний веб-сервер ----
logger.info("===== КРОК 2: POST /api/generate, qwen3:4b, 'Столиця України?' =====")
log_response(generate("qwen3:4b", "Столиця України?"))

# прогрів: обидві моделі вже в пам'яті, load_duration не спотворює виміри
for model in MODELS:
    generate(model, "розігрів")

# ---- Завдання 1, крок 1: просте фактичне питання ----
logger.info("===== ЗАВДАННЯ 1, КРОК 1: фактичне питання =====")
for model in MODELS:
    logger.info(f"--- {model} | {FACT}")
    log_response(generate(model, FACT))

# ---- Завдання 1, крок 2: задача на міркування, по 5 разів ----
logger.info("===== ЗАВДАННЯ 1, КРОК 2: задача на міркування (5 запусків) =====")
for model in MODELS:
    runs = []
    for i in range(1, 6):
        d = generate(model, LOGIC)
        m = metrics(d)
        runs.append(m)
        logger.info(f"--- {model} | запуск {i} | {m}")
        logger.info(f"response: {d['response']}")
        if d.get("thinking"):
            logger.info(f"thinking: {len(d['thinking'])} симв.")
    logger.info(f"### {model} середнє з 5: "
                f"eval_count={statistics.mean(r['eval_count'] for r in runs):.1f}, "
                f"час={statistics.mean(r['time_s'] for r in runs):.2f} с, "
                f"токенів/с={statistics.mean(r['tok_per_s'] for r in runs):.2f}")
