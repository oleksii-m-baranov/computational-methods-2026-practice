
"""Скорочення історії повідомлень."""


def drop_orphan_tools(messages):
    """Видаляє відповіді інструментів без відповідного виклику асистента."""

    valid_tool_ids = set()

    for message in messages:
        if message.get("role") == "assistant":
            for call in message.get("tool_calls") or []:
                valid_tool_ids.add(call.get("id"))

    result = []

    for message in messages:
        if message.get("role") == "tool":
            tool_id = message.get("tool_call_id")

            if tool_id not in valid_tool_ids:
                continue

        result.append(message)

    return result


def trim(messages, keep_last):
    """Зберігає системну інструкцію, запит і цілі групи викликів інструментів."""

    if len(messages) <= 2:
        return messages[:]

    head = messages[:2]
    history = messages[2:]

    start = max(0, len(history) - keep_last)

    # Не починаємо історію з відповіді інструмента.
    while start > 0 and (
        history[start].get("role") == "tool"
        or history[start - 1].get("role") == "tool"
    ):
        start -= 1

    tail = history[start:]

    # Видаляємо відповіді інструментів без відповідних викликів.
    tail = drop_orphan_tools(tail)

    return head + tail
