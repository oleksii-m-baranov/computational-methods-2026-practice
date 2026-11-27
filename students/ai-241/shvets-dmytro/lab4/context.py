
"""Безпечне обрізання історії агента."""


def trim(messages, keep_last):
    # Завжди зберігаємо системну інструкцію та задачу.
    head = messages[:2]
    history = messages[2:]

    # Розділяємо історію на цілі блоки:
    # assistant із tool_calls + усі відповіді tool.
    groups = []
    current = []

    for message in history:
        role = message["role"]

        if role == "tool":
            if current:
                current.append(message)
            continue

        if current:
            groups.append(current)

        current = [message]

    if current:
        groups.append(current)

    # Залишаємо останні цілі блоки в межах keep_last.
    selected = []
    count = 0

    for group in reversed(groups):
        if selected and count + len(group) > keep_last:
            break

        selected.insert(0, group)
        count += len(group)

    tail = [
        message
        for group in selected
        for message in group
    ]

    return head + tail
