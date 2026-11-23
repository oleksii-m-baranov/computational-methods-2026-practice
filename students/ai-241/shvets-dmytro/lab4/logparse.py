
"""Читання логів агента."""
import re


def parse_log(text):
    # Прибираємо префікси логера, включно з мілісекундами
    text = re.sub(
        r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:,\d+)?"
        r" - [A-Z]+ - ",
        "",
        text,
        flags=re.M
    )

    blocks = re.split(r"^ЗАДАЧА: ", text, flags=re.M)[1:]
    runs = []

    for block in blocks:
        chunks = re.split(r"^--- крок ", block, flags=re.M)[1:]
        steps = []

        for chunk in chunks:
            first = chunk.split("\n", 1)[0]
            number = re.match(r"\d+", first)
            prompt = re.search(r"prompt_tokens=(\d+)", first)
            completion = re.search(r"completion_tokens=(\d+)", first)
            squeeze = re.search(
                r"^\s*СТИСНЕННЯ: вхід був (\d+) токенів,"
                r" повідомлень (\d+) -> (\d+)",
                chunk,
                flags=re.M
            )

            steps.append({
                "n": int(number.group()) if number else 0,
                "tokens": int(prompt.group(1)) if prompt else None,
                "completion": int(completion.group(1)) if completion else 0,
                "calls": re.findall(
                    r"^\s*виклик\s*:\s*(.*)$",
                    chunk,
                    flags=re.M
                ),
                "from_cache": "з кешу" in first,
                "squeeze": (
                    tuple(map(int, squeeze.groups()))
                    if squeeze else None
                ),
                "answer": bool(re.search(
                    r"^ВІДПОВІДЬ:", chunk, flags=re.M
                )),
            })

        if "ПОМИЛКА СЕРВЕРА" in block:
            status = "server_error"
        elif re.search(r"^ВІДПОВІДЬ:", block, flags=re.M):
            status = "final"
        elif "СТОП: модель не змогла" in block:
            status = "retry_limit"
        elif "СТОП: вичерпано ліміт кроків" in block:
            status = "step_limit"
        else:
            status = "unknown"

        runs.append({
            "status": status,
            "steps": steps
        })

    return runs
