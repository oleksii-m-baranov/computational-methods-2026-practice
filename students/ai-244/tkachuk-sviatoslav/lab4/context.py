"""Обрізання історії зі збереженням зв'язків між викликами."""


def trim(messages, keep_last):
    head = messages[:2]
    tail = messages[2:][-keep_last:] if keep_last > 0 else []
    while tail and tail[0]["role"] == "tool":
        tail = tail[1:]
    return head + tail
