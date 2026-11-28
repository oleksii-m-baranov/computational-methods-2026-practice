import json

from task_progress import TaskProgress


with open("long_task.json", encoding="utf-8") as file:
    task = json.load(file)


progress = TaskProgress(task)

for item in task["expected"]["details"]:
    model = item["model"]
    price = item["price"]

    progress.record(
        "search_laptops",
        json.dumps({"query": model}),
        "ok"
    )

    progress.record(
        "laptop_info",
        json.dumps({"model": model}),
        "ok"
    )

    progress.record(
        "calc_installment",
        json.dumps({
            "price": price,
            "months": 12,
            "overpay_percent": 10
        }),
        "ok"
    )


print("УСПІШНИХ ВИКЛИКІВ:", progress.successful_calls)
print("УСІ МОДЕЛІ ОБРОБЛЕНІ:", progress.is_complete())
print("НЕВИКОНАНІ ОПЕРАЦІЇ:", progress.missing())
print("ПІДСУМОК:", progress.summary())

assert progress.successful_calls == 18
assert progress.is_complete()
assert progress.missing() == []

print("ТЕСТ ПРОЙДЕНО")
