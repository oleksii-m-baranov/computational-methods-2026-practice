
"""Скорочення історії переказом: стару частину переказує сама модель."""

import config
from model import client
from cache import ask_model


def split_history(messages, keep_last):
    """Ділить історію на початок, стару частину та останні повідомлення."""

    head = messages[:2]
    rest = messages[2:]

    cut = max(len(rest) - keep_last, 0)

    # Не починаємо останню частину з відповіді інструмента.
    while cut < len(rest) and rest[cut].get("role") == "tool":
        cut += 1

    return head, rest[:cut], rest[cut:]


def render_messages(messages):
    """Перетворює повідомлення на звичайний текст."""

    lines = []

    for message in messages:
        body = message.get("content") or message.get("tool_calls")
        lines.append(f"[{message['role']}] {body}")

    return "\n".join(lines)


def summarize(old_messages):
    """Переказує стару частину історії через модель із підтримкою кешу."""

    if not old_messages:
        return "", 0

    request = (
        "Стисло перекажи, що вже зроблено в цій роботі. "
        "Збережи всі точні числа, назви й результати інструментів без змін:\n"
        + render_messages(old_messages)
    )

    response, _ = ask_model(
        client,
        model=config.MODEL,
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": request,
            }
        ],
    )

    used = (
        response.usage.prompt_tokens
        + response.usage.completion_tokens
    )

    summary_text = response.choices[0].message.content

    return summary_text, used


def compress_by_summary(messages, used, logger):
    """Замінює стару частину історії коротким переказом."""

    before = len(messages)

    head, old, tail = split_history(
        messages,
        config.KEEP_LAST,
    )

    # Якщо старої історії немає, нічого не стискаємо.
    if not old:
        return messages

    text, extra = summarize(old)

    # Додаємо підсумок до початкового запитання.
    question = (
        head[1]["content"]
        + "\n\nПідсумок попередніх кроків: "
        + text
    )

    messages = [
        head[0],
        {
            "role": "user",
            "content": question,
        },
    ] + tail

    logger.info(
        f"  СТИСНЕННЯ: вхід був {used} токенів, "
        f"повідомлень {before} -> {len(messages)}, "
        f"підсумовування коштувало {extra} токенів"
    )

    logger.info(
        "  ПІДСУМОК ІСТОРІЇ:\n" + text
    )

    return messages
