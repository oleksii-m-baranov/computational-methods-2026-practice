
"""Окремий тест виправлення помилки агента."""

from langfuse import get_client, propagate_attributes

from agent import run_agent

question = (
    "Потрібно дізнатися вік першого комплексного щеплення "
    "та його ціну за допомогою інструмента vaccine_info. "
    "Для перевірки обробки помилок спочатку виклич vaccine_info "
    "з аргументом vaccine='комплексне щеплення'. "
    "Якщо інструмент поверне помилку і список допустимих назв, "
    "не завершуй відповідь і не проси користувача уточнювати назву. "
    "Знайди у списку назву 'комплексне', повторно виклич vaccine_info "
    "з виправленим аргументом vaccine='комплексне' "
    "і лише після успішного результату дай відповідь про вік і ціну."
)

with propagate_attributes(
    trace_name="recovery-demo",
    tags=["recovery-demo"],
):
    result = run_agent(question)

get_client().flush()

print("\nРезультат тесту:", result)

