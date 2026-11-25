import config
from langfuse.openai import OpenAI

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)


def split_history(messages, keep_last):

    head = messages[:2]
    rest = messages[2:]
    cut = max(len(rest) - keep_last, 0)
    while cut < len(rest) and rest[cut].get("role") == "tool":
        cut = cut + 1
    return head, rest[:cut], rest[cut:]


def render_messages(messages):

    lines = []
    for m in messages:
        body = m.get("content") or str(m.get("tool_calls") or "")
        role = m.get("role", "unknown")
        lines.append(f"[{role}] {body}")
    return "\n".join(lines)


def summarize(old_messages):

    request = (
            "Стисло перекажи, що вже зроблено в цій роботі. Збережи всі точні числа, "
            "назви й результати інструментів без змін:\n" + render_messages(old_messages)
    )
    response = client.chat.completions.create(
        model=config.MODEL, temperature=0,
        messages=[{"role": "user", "content": request}]
    )
    usage = response.usage
    used = (usage.prompt_tokens if usage else 0) + (usage.completion_tokens if usage else 0)
    content = response.choices[0].message.content or ""
    return content, used


def compress_by_summary(messages, used, logger):
    before = len(messages)
    head, old, tail = split_history(messages, config.KEEP_LAST)
    text, extra = summarize(old)

    question = (head[1].get("content", "") if len(head) > 1 else "") + "\n\nПідсумок попередніх кроків: " + text
    new_head_1 = {"role": "user", "content": question}
    messages = [head[0], new_head_1] + tail

    logger.info(f"СТИСНЕННЯ: вхід був {used} токенів, повідомлень {before} -> {len(messages)}"
                f", підсумовування коштувало {extra} токенів")
    logger.info(f"ПІДСУМОК ІСТОРІЇ:\n" + text)
    return messages