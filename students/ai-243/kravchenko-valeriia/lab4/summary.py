"""Скорочення історії переказом: стару частину переказує сама модель."""
import config
from model import client


def split_history(messages, keep_last):
    head = messages[:2]
    rest = messages[2:]
    cut = max(len(rest) - keep_last, 0)
    while cut < len(rest) and rest[cut]["role"] == "tool":
        cut = cut + 1
    return head, rest[:cut], rest[cut:]


def render_messages(messages):
    lines = []
    for m in messages:
        body = m.get("content") or m.get("tool_calls")
        lines.append(f"[{m['role']}] {body}")
    return "\n".join(lines)


def summarize(old_messages):
    request = ("Стисло перекажи, що вже зроблено в цій роботі. Збережи всі точні числа, "
               "назви й результати інструментів без змін:\n" + render_messages(old_messages))
    response = client.chat.completions.create(
        model=config.MODEL, temperature=0,
        messages=[{"role": "user", "content": request}])
    used = response.usage.prompt_tokens + response.usage.completion_tokens
    return response.choices[0].message.content, used


def compress_by_summary(messages, used, logger):
    before = len(messages)
    head, old, tail = split_history(messages, config.KEEP_LAST)
    text, extra = summarize(old)
    question = head[1]["content"] + "\n\nПідсумок попередніх кроків: " + text
    messages = [head[0], {"role": "user", "content": question}] + tail
    logger.info(f"  СТИСНЕННЯ: вхід був {used} токенів, повідомлень {before} -> {len(messages)}"
        f", підсумовування коштувало {extra} токенів")
    logger.info("  ПІДСУМОК ІСТОРІЇ:\n" + text)
    return messages