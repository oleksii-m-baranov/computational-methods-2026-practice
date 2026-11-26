import re


def find_status(block):
    if "ПОМИЛКА СЕРВЕРА" in block:
        return "server_error"
    if re.search(r"^ВІДПОВІДЬ:", block, flags=re.M):
        return "final"
    if "Стоп: модель не змогла" in block:
        return "retry_limit"
    if "Стоп: вичерпано ліміт кроків" in block:
        return "step_limit"
    return "unknown"


def parse_step(chunk):
    first_line = chunk.split("\n", 1)[0]

    step_num_match = re.search(r'крок\s*(\d+)', first_line, re.IGNORECASE)
    if not step_num_match:
        step_num_match = re.search(r'(\d+)', first_line)
    step_n = int(step_num_match.group(1)) if step_num_match else 1

    prompt = re.search(r"prompt_tokens=(\d+)", first_line)
    completion = re.search(r"completion_tokens=(\d+)", first_line)
    squeeze = re.search(r"^СТИСНЕННЯ: вхід був (\d+) токенів, повідомлень (\d+) -> (\d+)", chunk, flags=re.M)
    extra = re.findall(r"підсумовування коштувало (\d+) токенів", chunk)

    return {
        "n": step_n,
        "tokens": int(prompt.group(1)) if prompt else None,
        "completion": int(completion.group(1)) if completion else 0,
        "from_cache": "з кешу" in first_line,
        "calls": re.findall(r"виклик: (.*)", chunk),
        "answer": bool(re.search(r"^ВІДПОВІДЬ:", chunk, flags=re.M)),
        "server_error": "ПОМИЛКА СЕРВЕРА" in first_line,
        "squeeze": tuple(int(x) for x in squeeze.groups()) if squeeze else None,
        "extra": sum(int(x) for x in extra),
    }


def parse_run(block):
    chunks = re.split(r"(?=крок \d+)", block, flags=re.I)
    if len(chunks) <= 1:
        chunks = re.split(r"--- крок", block, flags=re.M)
    if len(chunks) > 1:
        chunks = chunks[1:]
    else:
        chunks = [block]

    return {
        "task": block.split("\n", 1)[0],
        "status": find_status(block),
        "steps": [parse_step(chunk) for chunk in chunks if chunk.strip()],
    }


def parse_log(text):
    text = re.sub(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} - [A-Z]+ - ", "", text, flags=re.M)
    blocks = re.split(r"^ЗАДАЧА: ", text, flags=re.M)
    if len(blocks) > 1:
        blocks = blocks[1:]
    else:
        blocks = [text]
    return [parse_run(block) for block in blocks]