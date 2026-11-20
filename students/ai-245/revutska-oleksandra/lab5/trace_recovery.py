from langfuse import observe, get_client, propagate_attributes
from dispatcher import call_tool


@observe(name="recovery_demo")
def recovery_demo():
    print("=== ПЕРШИЙ ВИКЛИК: ПОМИЛКА ===")

    level1, result1 = call_tool(
        "book_info",
        '{"title": "Неіснуюча книжка"}'
    )

    print("Рівень:", level1)
    print("Результат:", result1)

    print("\n=== ДРУГИЙ ВИКЛИК: ВИПРАВЛЕННЯ ===")

    level2, result2 = call_tool(
        "book_info",
        '{"title": "Основи алгоритмів"}'
    )

    print("Рівень:", level2)
    print("Результат:", result2)


with propagate_attributes(
    trace_name="checks-recovery-demo",
    tags=["checks", "recovery-demo"],
):
    recovery_demo()

get_client().flush()