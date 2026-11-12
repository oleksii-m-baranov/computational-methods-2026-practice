"""Показники прогону, обчислені з журналу агента."""

import statistics

import config


def count_repeats(steps):
    """Рахує повторні виклики інструментів."""
    seen = set()
    repeats = 0

    for step in steps:
        for call in step["calls"]:
            if call in seen:
                repeats += 1
            seen.add(call)

    return repeats


def typical_growth(tokens):
    """Медіана додатних приростів входу моделі."""
    growth = [
        after - before
        for (_, before), (_, after) in zip(tokens, tokens[1:])
        if after > before
    ]

    return statistics.median(growth) if growth else 0


def find_stall(tokens, typical):
    """Шукає крок, на якому вхід майже перестав рости."""
    for (_, before), (number, after) in zip(
        tokens, tokens[1:]
    ):
        near_window = after >= 0.8 * config.NUM_CTX
        stopped = after - before <= 0.2 * typical

        if near_window and stopped:
            return number

    return None


def describe(run):
    """Обчислює показники одного прогону."""
    steps = run["steps"]

    tokens = [
        (s["n"], s["tokens"])
        for s in steps
        if s["tokens"] is not None
    ]

    typical = typical_growth(tokens)
    n = len(tokens)
    first = tokens[0][1] if tokens else 0

    return {
        "status": run["status"],
        "steps": n,
        "repeats": count_repeats(steps),
        "first_tokens": first,
        "typical_growth": typical,
        "max_tokens": max(
            (t for _, t in tokens),
            default=0,
        ),
        "prompt_tokens": sum(t for _, t in tokens),
        "completion_tokens": sum(
            s["completion"] for s in steps
        ),
        "extra_tokens": sum(
            s["extra"] for s in steps
        ),
        "formula": (
            n * first + typical * n * (n - 1) / 2
        ),
        "stall": find_stall(tokens, typical),
        "cache_hits": sum(
            1 for s in steps if s["from_cache"]
        ),
        "squeezes": [
            s for s in steps if s["squeeze"]
        ],
    }