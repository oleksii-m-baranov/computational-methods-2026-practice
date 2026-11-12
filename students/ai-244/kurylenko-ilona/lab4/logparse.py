"""Читання та розбір журналів прогонів агента."""

import re


def find_status(block):
    """Визначає статус завершення прогону."""
    if "ПОМИЛКА СЕРВЕРА" in block:
        return "server_error"
    if re.search(r"^ВІДПОВІДЬ:", block, flags=re.M):
        return "final"
    if "СТОП: модель не змогла" in block:
        return "retry_limit"
    if "СТОП: вичерпано ліміт кроків" in block:
        return "step_limit"
    return "unknown"


def parse_step(chunk):
    """Витягує показники одного кроку."""
    first_line = chunk.split("\n", 1)[0]

    prompt = re.search(r"prompt_tokens=(\d+)", first_line)
    completion = re.search(r"completion_tokens=(\d+)", first_line)

    squeeze = re.search(
        r"^  СТИСНЕННЯ: вхід був (\d+) токенів, повідомлень (\d+) -> (\d+)",
        chunk,
        flags=re.M,
    )

    extra = re.findall(
        r"підсумовування коштувало (\d+) токенів",
        chunk,
    )

    return {
        "n": int(re.match(r"\d+", chunk).group()),
        "tokens": int(prompt.group(1)) if prompt else None,
        "completion": int(completion.group(1)) if completion else 0,
        "from_cache": "з кешу" in first_line,
        "calls": re.findall(
            r"^  виклик   : (.*)$",
            chunk,
            flags=re.M,
        ),
        "answer": bool(
            re.search(r"^ВІДПОВІДЬ:", chunk, flags=re.M)
        ),
        "server_error": "ПОМИЛКА СЕРВЕРА" in first_line,
        "squeeze": (
            tuple(int(x) for x in squeeze.groups())
            if squeeze else None
        ),
        "extra": sum(int(x) for x in extra),
    }


def parse_run(block):
    """Розбирає один прогін на окремі кроки."""
    chunks = re.split(
        r"^--- крок ",
        block,
        flags=re.M,
    )[1:]

    return {
        "task": block.split("\n", 1)[0],
        "status": find_status(block),
        "steps": [parse_step(chunk) for chunk in chunks],
    }


def parse_log(text):
    """Розбирає текст журналу на окремі прогони."""
    text = re.sub(
        r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} - [A-Z]+ - ",
        "",
        text,
        flags=re.M,
    )

    blocks = re.split(
        r"^ЗАДАЧА: ",
        text,
        flags=re.M,
    )[1:]

    return [parse_run(block) for block in blocks]