from state import AgentState

state = AgentState()

key1 = state.save(
    "search_laptops",
    {"query": "StudyNova 14"},
    "StudyNova 14"
)

key2 = state.save(
    "laptop_info",
    {"model": "StudyNova 14"},
    "Ціна: 22000 грн, на складі: 5 шт., гарантія: 24 міс."
)

key3 = state.save(
    "calc_installment",
    {"price": 22000, "months": 12, "overpay_percent": 10},
    "2016.67 грн на місяць, усього 24200.0 грн"
)

print("Збережено результатів:", len(state.results))
print("Пошук:", state.short_result(key1))
print("Інформація:", state.short_result(key2))
print("Розстрочка:", state.short_result(key3))
print("Повний результат:", state.get(key3))

path = state.export()

print("Файл стану:", path)

assert len(state.results) == 3
assert state.get(key3)["tool"] == "calc_installment"
assert "2016.67" in state.get(key3)["result"]

print("STATE TEST: PASS")
