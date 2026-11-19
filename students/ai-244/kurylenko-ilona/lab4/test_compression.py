"""Діагностична перевірка скорочення історії ЛР4."""

import logging

import config
from compress import compress_history


class TestState:
    def render(self):
        return (
            "Результати вже виконаних викликів:\n"
            "- search_articles -> Кіт дряпає меблі\n"
            "- vaccine_info -> 650 грн\n"
            "- calc_food -> 1500 г"
        )


def make_messages():
    messages = [
        {"role": "system", "content": "Тестова інструкція"},
        {"role": "user", "content": "Тестова довга задача"},
    ]

    for i in range(1, 6):
        messages.append({
            "role": "assistant",
            "content": None,
            "tool_calls": [{
                "id": f"call_{i}",
                "type": "function",
                "function": {
                    "name": "search_articles",
                    "arguments": '{"query":"кіт"}',
                },
            }],
        })
        messages.append({
            "role": "tool",
            "tool_call_id": f"call_{i}",
            "content": f"Результат {i}",
        })

    return messages


def main():
    logger = logging.getLogger("compression_test")
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())

    original = make_messages()
    old_compress = config.COMPRESS
    old_state = config.USE_STATE

    try:
        for use_state in (False, True):
            config.COMPRESS = "trim"
            config.USE_STATE = use_state

            name = "trim+state" if use_state else "trim"

            print(f"\nКОНФІГУРАЦІЯ: {name}")
            print("Повідомлень до:", len(original))

            result = compress_history(
                make_messages(),
                "Тестова довга задача",
                config.COMPRESS_AT + 100,
                TestState(),
                logger,
            )

            print("Повідомлень після:", len(result))
            print(
                "Стан додано:",
                "Результати вже виконаних викликів"
                in result[1]["content"],
            )

            assert len(result) < len(original)
            assert result[0]["role"] == "system"
            assert result[1]["role"] == "user"
            assert (
                "Результати вже виконаних викликів"
                in result[1]["content"]
            ) == use_state

            print("ТЕСТ ПРОЙДЕНО")

    finally:
        config.COMPRESS = old_compress
        config.USE_STATE = old_state


if __name__ == "__main__":
    main()