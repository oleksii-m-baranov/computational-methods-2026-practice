from dispatcher import call_tool

cases = [
    ("calc_installment", '{"price": 100, "months": 6'),                                 # зламаний JSON
    ("calc_installment", '{"price": "сто", "months": 6, "overpay_percent": 10}'),       # неправильний тип
    ("calc_installment", '{"price": 25000}'),                                           # немає обов'язкового поля
    ("calc_installment", '{"price": 25000, "months": 6, "overpay_percent": 10, "x": 1}'), # вигадане поле
    ("delete_all", '{}'),                                                               # неіснуючий інструмент
    ("place_order", '{"model": "StudyBook 14"}'),                                       # заборонена дія
    ("laptop_info", '{"model": "MacBook Pro"}'),                                        # Значення немає в довіднику
    ("calc_installment", '{"price": -500, "months": 6, "overpay_percent": 10}'),        # Значення поза межами
]

for name, raw in cases:
    level, text = call_tool(name, raw)
    print(f"{level:10} | {text}\n")