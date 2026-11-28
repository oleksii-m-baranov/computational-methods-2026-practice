import statistics
import sys

import config
from logparse import parse_log


def calculate_metrics(run, num_ctx=None):
    if num_ctx is None:
        num_ctx = config.NUM_CTX

    tokens = run["prompt_tokens"]
    completion = run.get("completion_tokens", [])

    maximum = max(tokens, default=0)
    minimum = min(tokens, default=0)

    deltas = [
        tokens[i] - tokens[i - 1]
        for i in range(1, len(tokens))
    ]

    median_delta = (
        statistics.median(deltas)
        if deltas
        else 0
    )

    first_prompt = tokens[0] if tokens else 0
    steps = len(tokens)

    predicted_total = (
        steps * first_prompt
        + median_delta * steps * (steps - 1) / 2
    )

    context_percent = (
        maximum / num_ctx * 100
        if num_ctx > 0
        else 0
    )

    return {
        "steps": run["steps"],
        "tool_calls": run["tool_calls"],
        "repeated_calls": run.get("repeated_calls", 0),
        "total_prompt_tokens": sum(tokens),
        "total_completion_tokens": sum(completion),
        "max_prompt_tokens": maximum,
        "min_prompt_tokens": minimum,
        "first_prompt_tokens": first_prompt,
        "context_usage_percent": round(context_percent, 2),
        "context_growth": maximum - minimum,
        "context_overflow": maximum >= num_ctx,
        "tokens_per_step": tokens,
        "deltas": deltas,
        "median_delta": median_delta,
        "predicted_total_tokens": round(predicted_total, 2),
        "actual_total_tokens": sum(tokens),
        "compressions": run.get("compressions", 0),
        "cache_hits": run.get("cache_hits", 0),
        "cache_misses": run.get("cache_misses", 0),
        "has_answer": run.get("has_answer", False),
        "stopped": run.get("stopped", False)
    }


def main():
    path = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "lab4.log"
    )

    runs = parse_log(path)

    print(f"Файл: {path}")
    print(f"Знайдено запусків: {len(runs)}")

    for index, run in enumerate(runs, 1):
        metrics = calculate_metrics(run)

        print(f"\nЗапуск {index}")
        print(f"Кроків: {metrics['steps']}")
        print(f"Викликів інструментів: {metrics['tool_calls']}")
        print(f"Повторних викликів: {metrics['repeated_calls']}")
        print(f"Перший prompt: {metrics['first_prompt_tokens']}")
        print(f"Токени за кроками: {metrics['tokens_per_step']}")
        print(f"Прирости: {metrics['deltas']}")
        print(f"Медіанний приріст: {metrics['median_delta']}")
        print(f"Сума вхідних токенів: {metrics['total_prompt_tokens']}")
        print(f"Сума вихідних токенів: {metrics['total_completion_tokens']}")
        print(f"Прогноз токенів: {metrics['predicted_total_tokens']}")
        print(f"Максимум токенів: {metrics['max_prompt_tokens']}")
        print(f"Використання контексту: {metrics['context_usage_percent']}%")
        print(f"Переповнення: {metrics['context_overflow']}")
        print(f"Стиснень: {metrics['compressions']}")
        print(f"Cache HIT: {metrics['cache_hits']}")
        print(f"Cache MISS: {metrics['cache_misses']}")
        print(f"Є відповідь: {metrics['has_answer']}")
        print(f"Зупинка: {metrics['stopped']}")


if __name__ == "__main__":
    main()
