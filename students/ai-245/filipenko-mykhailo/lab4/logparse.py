import re
import sys
from pathlib import Path


STEP_PATTERN = re.compile(
    r"--- крок\s+(\d+).*?"
    r"prompt_tokens=(\d+).*?"
    r"completion_tokens=(\d+)"
)

CALL_PATTERN = re.compile(
    r"виклик\s*:\s*([a-zA-Z_]+)\((.*)\)"
)


def parse_block(block):
    steps = []
    calls = []
    cache_hits = 0
    cache_misses = 0

    for line in block.splitlines():
        step_match = STEP_PATTERN.search(line)

        if step_match:
            steps.append({
                "step": int(step_match.group(1)),
                "prompt_tokens": int(step_match.group(2)),
                "completion_tokens": int(step_match.group(3))
            })

        call_match = CALL_PATTERN.search(line)

        if call_match:
            calls.append({
                "name": call_match.group(1),
                "arguments": call_match.group(2)
            })

        if "КЕШ: HIT" in line:
            cache_hits += 1

        if "КЕШ: MISS" in line:
            cache_misses += 1

    prompt_tokens = [
        item["prompt_tokens"]
        for item in steps
    ]

    completion_tokens = [
        item["completion_tokens"]
        for item in steps
    ]

    call_keys = [
        (item["name"], item["arguments"])
        for item in calls
    ]

    repeated_calls = len(call_keys) - len(set(call_keys))

    return {
        "steps": len(steps),
        "step_details": steps,
        "tool_calls": len(calls),
        "tool_names": [item["name"] for item in calls],
        "tool_details": calls,
        "repeated_calls": repeated_calls,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "max_prompt_tokens": max(prompt_tokens, default=0),
        "total_prompt_tokens": sum(prompt_tokens),
        "total_completion_tokens": sum(completion_tokens),
        "compressions": len(
            re.findall(r"СТИСНЕННЯ:", block)
        ),
        "cache_hits": cache_hits,
        "cache_misses": cache_misses,
        "stopped": "СТОП:" in block,
        "has_answer": "ВІДПОВІДЬ:" in block
    }


def parse_log(path="lab4.log"):
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Файл не знайдено: {file_path}"
        )

    text = file_path.read_text(encoding="utf-8-sig")

    blocks = re.split(
        r"(?:^|\n)={20,}\s*\n",
        text
    )

    runs = []

    for block in blocks:
        if "ЗАДАЧА:" not in block:
            continue

        runs.append(parse_block(block))

    return runs


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "lab4.log"

    runs = parse_log(path)

    print(f"Файл: {path}")
    print(f"Знайдено запусків: {len(runs)}")

    for index, run in enumerate(runs, 1):
        print(f"\nЗапуск {index}")
        print(f"Кроків: {run['steps']}")
        print(f"Викликів інструментів: {run['tool_calls']}")
        print(f"Повторних викликів: {run['repeated_calls']}")
        print(f"Вхідні токени: {run['prompt_tokens']}")
        print(f"Вихідні токени: {run['completion_tokens']}")
        print(f"Максимум вхідних токенів: {run['max_prompt_tokens']}")
        print(f"Сума вхідних токенів: {run['total_prompt_tokens']}")
        print(f"Сума вихідних токенів: {run['total_completion_tokens']}")
        print(f"Стиснень: {run['compressions']}")
        print(f"Cache HIT: {run['cache_hits']}")
        print(f"Cache MISS: {run['cache_misses']}")
        print(f"Є відповідь: {run['has_answer']}")
        print(f"Зупинка: {run['stopped']}")
