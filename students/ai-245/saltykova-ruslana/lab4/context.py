
def drop_orphan_tools(tail):

    while tail and tail[0]["role"] == "tool":
        tail = tail[1:]
    return tail

def trim(messages, keep_last):

    head = messages[:2]                     # перші два повідомлення
    tail = messages[2:][-keep_last:]        # з решти беремо лише останні keep_last
    tail = drop_orphan_tools(tail)          # не починаємо «хвіст» з результату без виклику
    return head + tail