
"""Обчислення метрик використання контексту агента."""

import config


def calculate_metrics(parsed_log):
    """Обчислює показники за результатами аналізу лога."""

    steps = parsed_log["steps"]

    prompt_tokens = [
        step["prompt_tokens"]
        for step in steps
    ]

    completion_tokens = [
        step["completion_tokens"]
        for step in steps
    ]

    first_prompt = prompt_tokens[0] if prompt_tokens else 0
    last_prompt = prompt_tokens[-1] if prompt_tokens else 0

    growth = last_prompt - first_prompt

    context_usage = (
        last_prompt / config.NUM_CTX * 100
        if config.NUM_CTX > 0
        else 0
    )

    return {
        "steps": len(steps),
        "tool_calls": parsed_log["tool_calls"],
        "first_prompt_tokens": first_prompt,
        "last_prompt_tokens": last_prompt,
        "max_prompt_tokens": parsed_log["max_prompt_tokens"],
        "prompt_growth": growth,
        "total_completion_tokens": sum(completion_tokens),
        "context_usage_percent": round(context_usage, 2),
    }
