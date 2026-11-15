"""Демонстрація самовиправлення агента без підказування помилки."""

from langfuse import get_client, propagate_attributes

from agent import run_agent


questions = [
    "Скільки коштує щеплення проти сказу і коли його вперше роблять?",
    "Скільки корму треба коту вагою 4500 грамів на 2 тижні?",
]


for index, question in enumerate(questions, start=1):
    print(f"\n{'=' * 60}")
    print(f"СЦЕНАРІЙ {index}: {question}")

    with propagate_attributes(
        trace_name=f"recovery-{index}",
        tags=["recovery"]
    ):
        result = run_agent(question)

    print(f"\nРезультат сценарію {index}: {result}")


get_client().flush()
