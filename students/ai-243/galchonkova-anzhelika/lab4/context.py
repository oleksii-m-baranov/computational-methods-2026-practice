"""Скорочення історії повідомлень."""


def drop_orphan_tools(tail):
    """Прибирає з початку списку «осиротілі» результати інструментів."""
    while tail and tail[0]["role"] == "tool":
        tail = tail[1:]
    return tail


def trim(messages, keep_last):
    """Скорочує історію: лишає початок (system + user) і останні keep_last повідомлень."""
    head = messages[:2]
    tail = messages[2:][-keep_last:]
    tail = drop_orphan_tools(tail)
    return head + tail
