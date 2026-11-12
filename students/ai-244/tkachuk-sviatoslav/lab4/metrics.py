"""Показники токенів, стиснень і повторних викликів."""
import statistics
import config


def describe(run):
    steps = run["steps"]
    token_pairs = [(s["n"], s["tokens"]) for s in steps if s["tokens"] is not None]
    increments = [b[1] - a[1] for a, b in zip(token_pairs, token_pairs[1:]) if b[1] > a[1]]
    growth = statistics.median(increments) if increments else 0
    stall = None
    for (_, before), (number, after) in zip(token_pairs, token_pairs[1:]):
        if after >= 0.8 * config.NUM_CTX and after - before <= 0.2 * growth:
            stall = number
            break
    seen = set()
    repeats = 0
    for step in steps:
        for call in step["calls"]:
            repeats += int(call in seen)
            seen.add(call)
    n = len(token_pairs)
    first = token_pairs[0][1] if token_pairs else 0
    return {
        "status": run["status"], "steps": len(steps), "model_calls": n,
        "tool_calls": sum(len(s["calls"]) for s in steps),
        "repeats": repeats,
        "first_tokens": first,
        "typical_growth": growth,
        "max_tokens": max((v for _, v in token_pairs), default=0),
        "prompt_tokens": sum(v for _, v in token_pairs),
        "completion_tokens": sum(s["completion"] for s in steps),
        "extra_tokens": sum(s["extra"] for s in steps),
        "formula": n * first + growth * n * (n-1) / 2,
        "stall": stall,
        "cache_hits": sum(int(s["from_cache"]) for s in steps),
        "squeezes": [s for s in steps if s["squeeze"]],
    }
