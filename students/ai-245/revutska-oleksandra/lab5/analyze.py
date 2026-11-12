
"""Аналіз використання контексту агента в лабораторній №4."""

import sys

from logparse import parse_log
from metrics import calculate_metrics


def main():
    if len(sys.argv) != 3:
        print("Використання: python analyze.py <log_file> <mode>")
        sys.exit(1)

    log_file = sys.argv[1]
    mode = sys.argv[2]

    if mode != "steps":
        print(f"Невідомий режим аналізу: {mode}")
        sys.exit(1)

    parsed = parse_log(log_file)
    metrics = calculate_metrics(parsed)

    print("\n=== АНАЛІЗ КОНТЕКСТУ АГЕНТА ===")
    print(f"Файл: {log_file}")
    print(f"Кількість кроків: {metrics['steps']}")
    print(f"Виклики інструментів: {metrics['tool_calls']}")
    print(f"Перший prompt: {metrics['first_prompt_tokens']}")
    print(f"Останній prompt: {metrics['last_prompt_tokens']}")
    print(f"Максимум prompt: {metrics['max_prompt_tokens']}")
    print(f"Приріст токенів: {metrics['prompt_growth']}")
    print(f"Вихідні токени: {metrics['total_completion_tokens']}")
    print(
        f"Використання контексту: "
        f"{metrics['context_usage_percent']}%"
    )

    print("\n=== ТОКЕНИ ЗА КРОКАМИ ===")

    for step in parsed["steps"]:
        print(
            f"Крок {step['step']}: "
            f"prompt={step['prompt_tokens']}, "
            f"completion={step['completion_tokens']}"
        )


if __name__ == "__main__":
    main()
