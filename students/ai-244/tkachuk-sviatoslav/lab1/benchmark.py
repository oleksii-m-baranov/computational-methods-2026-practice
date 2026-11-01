"""Завдання 4: справжній TTFT першого видимого тексту, прогрів, 3 повтори, медіани."""
import statistics
import time
from config import ROOT, PROMPTS
from common import native_request, save_json, save_csv, safe_error, now
from providers import PROVIDERS, make_client

FIELDS = ["provider", "model", "prompt", "ttft_s", "total_s", "chars_per_s", "runs_ok"]
RAW_FIELDS = ["provider", "model", "prompt", "attempt", "status", "ttft_s", "total_s",
              "chars", "chars_per_s", "completion_tokens", "finish_reason", "error"]


def measure(client, model, prompt, clock=time.perf_counter):
    t0 = clock()
    first = None
    parts, finish, usage = [], None, {}
    stream = client.chat.completions.create(
        model=model, messages=[{"role": "user", "content": prompt}],
        temperature=0.7, max_tokens=4096, stream=True,
        stream_options={"include_usage": True},
    )
    try:
        for chunk in stream:
            if getattr(chunk, "usage", None):
                usage = chunk.usage.model_dump()
            # Завершальний пакет із usage зазвичай має choices=[].
            if not chunk.choices:
                continue
            choice = chunk.choices[0]
            if choice.finish_reason:
                finish = choice.finish_reason
            piece = choice.delta.content
            if piece:
                if first is None:
                    first = clock()
                parts.append(piece)
    finally:
        if hasattr(stream, "close"):
            stream.close()
    total = clock() - t0
    text = "".join(parts)
    return {
        "status": "ok" if first is not None and finish == "stop" else "incomplete",
        "ttft_s": first - t0 if first is not None else None,
        "total_s": total, "chars": len(text),
        "chars_per_s": len(text) / total if total > 0 else None,
        "completion_tokens": usage.get("completion_tokens"),
        "usage": usage, "finish_reason": finish, "response": text, "at": now(),
    }


def aggregate(rows):
    result = []
    for provider in ("local", "cloud"):
        for prompt in PROMPTS:
            good = [r for r in rows if r["provider"] == provider and r["prompt"] == prompt and r["status"] == "ok"]
            row = {"provider": provider, "model": PROVIDERS[provider]["model"],
                   "prompt": prompt, "runs_ok": len(good)}
            for key in ("ttft_s", "total_s", "chars_per_s"):
                # Неповний набір не видаємо за медіану трьох запусків.
                row[key] = statistics.median(r[key] for r in good) if len(good) == 3 else None
            result.append(row)
    return result


def run(out=ROOT, cold=True):
    rows, starts = [], []
    if cold:
        model = PROVIDERS["local"]["model"]
        try:
            # Синхронне вивантаження моделі ПЕРЕД холодним виміром, без прогріву між ними.
            native_request({"model": model, "keep_alive": 0, "stream": False})
            client, _ = make_client("local")
            with client:
                for label in ("cold", "warm"):
                    row = measure(client, model, PROMPTS["short"])
                    starts.append({"start": label, "model": model, **row})
        except Exception as exc:
            starts.append({"start": "cold/warm", "status": "error", "error": safe_error(exc)})
        save_json(out / "cold_warm.json", starts)
    for provider in ("local", "cloud"):
        model = PROVIDERS[provider]["model"]
        try:
            client, model = make_client(provider)
        except Exception as exc:
            for name in PROMPTS:
                for attempt in range(1, 4):
                    rows.append({"provider": provider, "model": model, "prompt": name,
                                 "attempt": attempt, "status": "error", "error": safe_error(exc)})
            continue
        with client:
            try:
                warmup = measure(client, model, "Напиши одне слово: готово.")
                save_json(out / f"warmup_{provider}.json", warmup)
                for name, prompt in PROMPTS.items():
                    for attempt in range(1, 4):
                        try:
                            row = measure(client, model, prompt)
                        except Exception as exc:
                            row = {"status": "error", "error": safe_error(exc)}
                        row.update(provider=provider, model=model, prompt=name, attempt=attempt)
                        rows.append(row)
                        save_json(out / "benchmark_raw.json", rows)
                        print(f"Завдання 4: {provider} / {name} / {attempt}: {row['status']}", flush=True)
            except Exception as exc:
                for name in PROMPTS:
                    for attempt in range(1, 4):
                        rows.append({"provider": provider, "model": model, "prompt": name,
                                     "attempt": attempt, "status": "error", "error": safe_error(exc)})
    save_json(out / "benchmark_raw.json", rows)
    save_csv(out / "results_raw.csv", rows, RAW_FIELDS)
    summary = aggregate(rows)
    save_csv(out / "results.csv", summary, FIELDS)
    return summary


if __name__ == "__main__":
    run()

