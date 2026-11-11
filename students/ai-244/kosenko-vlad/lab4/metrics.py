"""Показники прогону, які рахуються з розібраного лога (див. logparse.py)."""
import statistics

import config


def count_repeats(steps):
    """Рахує повторні виклики: той самий інструмент з тими самими аргументами, що вже були."""
    seen = set()                                  # виклики, які вже траплялися
    repeats = 0
    for step in steps:
        for call in step["calls"]:
            if call in seen:
                repeats += 1
            seen.add(call)
    return repeats


def typical_growth(tokens):
    """Типовий приріст входу за крок: медіана всіх додатних збільшень.

    tokens - список пар (номер кроку, prompt_tokens).
    """
    growth = [after - before
              for (_, before), (_, after) in zip(tokens, tokens[1:])
              if after > before]
    return statistics.median(growth) if growth else 0


def find_stall(tokens, typical):
    """Шукає крок, на якому вхід підійшов до межі вікна і майже не росте.

    Це ознака того, що сервер мовчки обрізає вхід.
    """
    for (_, before), (number, after) in zip(tokens, tokens[1:]):
        near_window = after >= 0.8 * config.NUM_CTX      # вхід уже займає понад 80% вікна
        stopped = after - before <= 0.2 * typical        # а росте менш ніж на п'яту частину норми
        if near_window and stopped:
            return number
    return None


def describe(run):
    """Збирає всі показники одного прогону в один словник."""
    steps = run["steps"]
    tokens = [(s["n"], s["tokens"]) for s in steps if s["tokens"] is not None]
    typical = typical_growth(tokens)
    n = len(tokens)
    first = tokens[0][1] if tokens else 0
    return {
        "status": run["status"],
        "steps": n,                                              # скільки разів викликали модель
        "repeats": count_repeats(steps),
        "first_tokens": first,                                   # вхід першого кроку
        "typical_growth": typical,
        "max_tokens": max((t for _, t in tokens), default=0),
        "prompt_tokens": sum(t for _, t in tokens),              # сума входів за прогін
        "completion_tokens": sum(s["completion"] for s in steps),
        "extra_tokens": sum(s["extra"] for s in steps),          # знадобиться в додатковому завданні
        "formula": n * first + typical * n * (n - 1) / 2,        # формула з лекції 7
        "stall": find_stall(tokens, typical),
        "cache_hits": sum(1 for s in steps if s["from_cache"]),
        "squeezes": [s for s in steps if s["squeeze"]],          # кроки, після яких історію скорочували
    }