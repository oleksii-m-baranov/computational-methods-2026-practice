
"""Аналіз покрокових логів агента для лабораторної №4."""

import re
from pathlib import Path


STEP_PATTERN = re.compile(
    r"---\s*крок\s+(\d+)\s*\|\s*"
    r"prompt_tokens=(\d+)\s*\|\s*"
    r"completion_tokens=(\d+)"
)

CALL_PATTERN = re.compile(r"виклик:\s*(\w+)\(")


def parse_log(path):
    """Зчитує кроки, токени та виклики інструментів."""

    path = Path(path)

    if not path.is_file():
        raise FileNotFoundError(f"Лог не знайдено: {path}")

    content = path.read_text(encoding="utf-8")

    steps = []

    for match in STEP_PATTERN.finditer(content):
        steps.append({
            "step": int(match.group(1)),
            "prompt_tokens": int(match.group(2)),
            "completion_tokens": int(match.group(3)),
        })

    calls = CALL_PATTERN.findall(content)

    return {
        "steps": steps,
        "tool_calls": len(calls),
        "tool_names": calls,
        "max_prompt_tokens": max(
            (step["prompt_tokens"] for step in steps),
            default=0,
        ),
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Використання: python logparse.py <шлях_до_лога>")
        sys.exit(1)

    result = parse_log(sys.argv[1])

    print("Кількість кроків:", len(result["steps"]))
    print("Кількість викликів інструментів:", result["tool_calls"])
    print("Максимум вхідних токенів:", result["max_prompt_tokens"])

    for step in result["steps"]:
        print(
            f"Крок {step['step']}: "
            f"prompt={step['prompt_tokens']}, "
            f"completion={step['completion_tokens']}"
        )
