"""Читання лога прогону: розбір тексту лога на прогони та кроки.

Лог - це звичайний текстовий файл, який пише агент. У ньому є рядки такого вигляду:
    --- крок 3 | помилок поспіль=0 | prompt_tokens=1250 | completion_tokens=30
      виклик   : search({"query": "..."})
      СТИСНЕННЯ: вхід був 2900 токенів, повідомлень 14 -> 8
    ВІДПОВІДЬ: ...
Скрипт шукає такі рядки за зразками (регулярними виразами) і складає з них числа.
"""
import re


def find_status(block):
    """Як закінчився прогін. Визначаємо за рядками, які агент пише наприкінці."""
    if "ПОМИЛКА СЕРВЕРА" in block:
        return "server_error"                    # сервер повернув помилку
    if re.search(r"^ВІДПОВІДЬ:", block, flags=re.M):
        return "final"                           # модель дала відповідь без виклику інструмента
    if "СТОП: модель не змогла" in block:
        return "retry_limit"                     # забагато помилок моделі поспіль
    if "СТОП: вичерпано ліміт кроків" in block:
        return "step_limit"                      # закінчилися кроки
    return "unknown"


def parse_step(chunk):
    """Розбирає один крок: текст від слів «--- крок» до наступного кроку."""
    first_line = chunk.split("\n", 1)[0]                          # заголовок кроку
    prompt = re.search(r"prompt_tokens=(\d+)", first_line)
    completion = re.search(r"completion_tokens=(\d+)", first_line)
    squeeze = re.search(r"^  СТИСНЕННЯ: вхід був (\d+) токенів, повідомлень (\d+) -> (\d+)",
                        chunk, flags=re.M)
    extra = re.findall(r"підсумовування коштувало (\d+) токенів", chunk)   # для додаткового завдання
    return {
        "n": int(re.match(r"\d+", chunk).group()),                # номер кроку
        "tokens": int(prompt.group(1)) if prompt else None,       # токенів на вході моделі
        "completion": int(completion.group(1)) if completion else 0,
        "from_cache": "з кешу" in first_line,                     # відповідь узято з кешу
        "calls": re.findall(r"^  виклик   : (.*)$", chunk, flags=re.M),   # виклики інструментів
        "answer": bool(re.search(r"^ВІДПОВІДЬ:", chunk, flags=re.M)),
        "server_error": "ПОМИЛКА СЕРВЕРА" in first_line,
        "squeeze": tuple(int(x) for x in squeeze.groups()) if squeeze else None,
        "extra": sum(int(x) for x in extra),
    }


def parse_run(block):
    """Розбирає один прогін: текст від слова «ЗАДАЧА:» до наступного прогону."""
    chunks = re.split(r"^--- крок ", block, flags=re.M)[1:]       # по одному шматку на крок
    return {
        "task": block.split("\n", 1)[0],                          # текст задачі
        "status": find_status(block),
        "steps": [parse_step(chunk) for chunk in chunks],
    }


def parse_log(text):
    """Ділить лог на прогони. У логу run_all.py їх п'ять, у логу measure.py - один."""
    # логер додає на початок рядка «2026-10-20 11:26:38 - INFO - », прибираємо його
    text = re.sub(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} - [A-Z]+ - ", "", text, flags=re.M)
    blocks = re.split(r"^ЗАДАЧА: ", text, flags=re.M)[1:]
    return [parse_run(block) for block in blocks]