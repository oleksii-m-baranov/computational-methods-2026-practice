"""Скорочення історії переказом за допомогою мовної моделі."""

import config
from model import client


def split_history(messages, keep_last):
    """Ділить історію на початок, стару частину та останні повідомлення."""
    head = messages[:2]
    rest = messages[2:]

    cut = max(len(rest) - keep_last, 0)

    # Не залишаємо результат інструмента без виклику.
    while cut < len(rest) and rest[cut]["role"] == "tool":
        cut += 1

    return head, rest[:cut], rest[cut:]


def render_messages(messages):
    """Перетворює повідомлення на текст для підсумовування."""
    lines = []

    for message in messages:
        body = message.get("content") or message.get("tool_calls")
        lines.append(f"[{message['role']}] {body}")

    return "\n".join(lines)


def summarize(old_messages):
    """Створює підсумок старої історії окремим викликом моделі."""
    request = (
        "Стисло перекажи, що вже зроблено в цій роботі. "
        "Збережи всі точні числа, назви й результати "
        "інструментів без змін:\n"
        + render_messages(old_messages)
    )

    response = client.chat.completions.create(
        model=config.MODEL,
        temperature=0,
        messages=[
            {"role": "user", "content": request}
        ],
    )

    used = (
        response.usage.prompt_tokens
        + response.usage.completion_tokens
    )

    return response.choices[0].message.content, used


def compress_by_summary(messages, used, logger):
    """Замінює стару історію стислим переказом."""
    before = len(messages)

    head, old, tail = split_history(
        messages,
        config.KEEP_LAST,
    )

    # Якщо немає старої частини, нічого підсумовувати.
    if not old:
        return messages

    text, extra = summarize(old)

    question = (
        head[1]["content"]
        + "\n\nПідсумок попередніх кроків: "
        + (text or "")
    )

    messages = [
        head[0],
        {"role": "user", "content": question},
    ] + tail

    logger.info(
        f"  СТИСНЕННЯ: вхід був {used} токенів, "
        f"повідомлень {before} -> {len(messages)}, "
        f"підсумовування коштувало {extra} токенів"
    )

    logger.info(
        "  ПІДСУМОК ІСТОРІЇ:\n" + (text or "")
    )

    return messages