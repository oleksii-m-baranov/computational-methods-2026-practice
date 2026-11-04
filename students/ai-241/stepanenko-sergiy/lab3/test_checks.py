
from dispatcher import call_tool

cases = [
    ("calc_installment", '{"price": 24000, "months": 6, "overpay_percent": 10'),          # зламаний JSON
    ("calc_installment", '{"price": "двадцять тисяч", "months": 6, "overpay_percent": 10}'),  # неправильний тип
    ("calc_installment", '{"price": 24000, "months": 6}'),                                 # немає поля
    ("laptop_info", '{"model": "StudyBook 14", "x": 1}'),                                    # вигадане поле
    ("delete_all", '{}'),                                                                  # неіснуючий інструмент
    ("place_order", '{"model": "StudyBook 14"}'),                                           # заборонена дія
    ("laptop_info", '{"model": "DevSphere 16"}'),                                           # немає в довіднику
    ("calc_installment", '{"price": -500, "months": 6, "overpay_percent": 10}'),            # значення поза межами
]

for name, raw in cases:
    level, text = call_tool(name, raw)
    print(f"{level:10} | {text}\n")