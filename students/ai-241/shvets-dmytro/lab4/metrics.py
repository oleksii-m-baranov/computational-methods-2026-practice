
"""Розрахунок метрик агента."""
import statistics
import config


def describe(run):
    steps = run["steps"]
    tokens = [
        (s["n"], s["tokens"])
        for s in steps if s["tokens"] is not None
    ]

    growth = [
        b[1] - a[1]
        for a, b in zip(tokens, tokens[1:])
        if b[1] > a[1]
    ]
    typical = statistics.median(growth) if growth else 0

    seen = set()
    repeats = 0
    for step in steps:
        for call in step["calls"]:
            if call in seen:
                repeats += 1
            seen.add(call)

    stall = None
    for a, b in zip(tokens, tokens[1:]):
        if (
            typical > 0
            and b[1] >= config.NUM_CTX * 0.8
            and b[1] - a[1] <= typical * 0.2
        ):
            stall = b[0]
            break

    first = tokens[0][1] if tokens else 0
    n = len(tokens)

    return {
        "status": run["status"],
        "steps": n,
        "first_tokens": first,
        "typical_growth": typical,
        "max_tokens": max((t for _, t in tokens), default=0),
        "prompt_tokens": sum(t for _, t in tokens),
        "completion_tokens": sum(
            s["completion"] for s in steps
        ),
        "formula": n * first + typical * n * (n - 1) / 2,
        "stall": stall,
        "repeats": repeats,
        "cache_hits": sum(s["from_cache"] for s in steps),
        "squeezes": [
            (s["n"], s["squeeze"])
            for s in steps if s["squeeze"]
        ],
        "calls": sum(len(s["calls"]) for s in steps),
    }
