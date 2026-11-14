"""Скорочення історії повідомлень."""


def drop_orphan_tools(tail):
    while tail and tail[0]["role"] == "tool":
        tail = tail[1:]
    return tail


def trim(messages, keep_last):
    head = messages[:2]
    tail = messages[2:][-keep_last:]
    tail = drop_orphan_tools(tail)
    return head + tail