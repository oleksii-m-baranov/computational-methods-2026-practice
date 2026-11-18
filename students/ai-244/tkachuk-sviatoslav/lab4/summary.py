"""Додатковий режим стиснення історії підсумовуванням."""
import config


def split_history(messages, keep_last):
    head = messages[:2]
    rest = messages[2:]
    cut = max(0, len(rest) - keep_last)
    while cut < len(rest) and rest[cut]["role"] == "tool":
        cut += 1
    return head, rest[:cut], rest[cut:]


def compress_by_summary(messages, used, logger):
    from model import client
    head, old, tail = split_history(messages, config.KEEP_LAST)
    if not old:
        return messages
    lines = [f"[{m['role']}] {m.get('content') or m.get('tool_calls')}" for m in old]
    request = ("Стисло підсумуй виконані кроки, точно зберігай числа та результати інструментів:\n"
               + "\n".join(lines))
    try:
        response = client.chat.completions.create(
            model=config.MODEL, temperature=0, messages=[{"role": "user", "content": request}]
        )
    except Exception as exc:
        logger.error(f"  ПОМИЛКА ПІДСУМОВУВАННЯ: {exc}")
        return messages
    extra = (response.usage.prompt_tokens + response.usage.completion_tokens) if response.usage else 0
    text = response.choices[0].message.content or ""
    updated = [head[0], {"role": "user", "content": head[1]["content"]
                                    + "\n\nПідсумок попередніх кроків: " + text}] + tail
    logger.info(f"  СТИСНЕННЯ: вхід був {used} токенів, повідомлень {len(messages)} -> {len(updated)}, "
                f"підсумовування коштувало {extra} токенів")
    logger.info("  ПІДСУМОК ІСТОРІЇ:\n" + text)
    return updated
