"""Перетворення текстових логів у записи кроків агента."""
import re


def parse_step(chunk):
    header = chunk.split("\n", 1)[0]
    prompt = re.search(r"prompt_tokens=(\d+)", header)
    completion = re.search(r"completion_tokens=(\d+)", header)
    squeeze = re.search(r"^  СТИСНЕННЯ: вхід був (\d+) токенів, повідомлень (\d+) -> (\d+)", chunk, re.M)
    return {
        "n": int(re.match(r"\d+", chunk).group()),
        "tokens": int(prompt.group(1)) if prompt else None,
        "completion": int(completion.group(1)) if completion else 0,
        "from_cache": "з кешу" in header,
        "calls": re.findall(r"^  виклик   : (.*)$", chunk, re.M),
        "results": re.findall(r"^  результат: (.*)$", chunk, re.M),
        "answer": bool(re.search(r"^ВІДПОВІДЬ:", chunk, re.M)),
        "server_error": "ПОМИЛКА СЕРВЕРА" in header,
        "squeeze": tuple(map(int, squeeze.groups())) if squeeze else None,
        "extra": sum(map(int, re.findall(r"підсумовування коштувало (\d+) токенів", chunk))),
    }


def parse_log(text):
    clean = re.sub(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} - [A-Z]+ - ", "", text, flags=re.M)
    blocks = re.split(r"^ЗАДАЧА: ", clean, flags=re.M)[1:]
    runs = []
    for block in blocks:
        chunks = re.split(r"^--- крок ", block, flags=re.M)[1:]
        status = "unknown"
        if "ПОМИЛКА СЕРВЕРА" in block:
            status = "server_error"
        elif re.search(r"^ВІДПОВІДЬ:", block, re.M):
            status = "final"
        elif "СТОП: модель не змогла" in block:
            status = "retry_limit"
        elif "СТОП: вичерпано ліміт кроків" in block:
            status = "step_limit"
        runs.append({"task": block.splitlines()[0], "status": status,
                     "steps": [parse_step(chunk) for chunk in chunks]})
    return runs
