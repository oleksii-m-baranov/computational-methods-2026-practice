
"""Керування історією повідомлень агента."""

import copy


def trim_messages(messages, keep_last=6):
    """
    Скорочує історію діалогу.

    Зберігає системну інструкцію, початкове завдання
    та останні групи повідомлень, не розриваючи
    виклики інструментів і відповіді на них.
    """

    if len(messages) <= 2:
        return copy.deepcopy(messages)

    # Незмінна частина контексту.
    prefix = copy.deepcopy(messages[:2])
    history = messages[2:]

    # Формуємо групи: повідомлення асистента
    # разом із відповідями викликаних інструментів.
    groups = []
    current_group = []

    for message in history:
        role = (
            message.get("role")
            if isinstance(message, dict)
            else getattr(message, "role", None)
        )

        if role == "assistant":
            if current_group:
                groups.append(current_group)
            current_group = [message]

        elif role == "tool":
            current_group.append(message)

        else:
            if current_group:
                groups.append(current_group)
            current_group = [message]

    if current_group:
        groups.append(current_group)

    # Залишаємо останні групи, орієнтуючись
    # на кількість повідомлень.
    selected = []
    count = 0

    for group in reversed(groups):
        if selected and count >= keep_last:
            break

        selected.insert(0, group)
        count += len(group)

    result = prefix

    for group in selected:
        result.extend(copy.deepcopy(group))

    return result
