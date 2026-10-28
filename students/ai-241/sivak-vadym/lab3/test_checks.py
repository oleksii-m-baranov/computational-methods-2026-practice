"""Перевірка ланцюжка перевірок диспетчера без моделі (табл. 2)."""
from dispatcher import call_tool

cases = [
    ("transport_info", '{"route": "Кам\'янець-Подільський"}'),                       # коректний виклик
    ("transport_info", '{"route": "Львів"'),                                         # зламаний JSON
    ("calc_budget", '{"price_per_person": "чотириста", "people": 3, "extra": 500}'),  # неправильний тип
    ("calc_budget", '{"price_per_person": 420, "people": 3}'),                       # немає поля
    ("transport_info", '{"route": "Львів", "date": "субота"}'),                      # вигадане поле
    ("delete_all", '{}'),                                                            # неіснуючий інструмент
    ("buy_ticket", '{"route": "Львів"}'),                                            # заборонена дія
    ("transport_info", '{"route": "Париж"}'),                                        # немає в довіднику
    ("calc_budget", '{"price_per_person": 420, "people": 0, "extra": 500}'),         # поза межами (клас)
    ("calc_budget", '{"price_per_person": 450, "people": 3, "extra": 500}'),         # ціни немає в довіднику
]

for name, raw in cases:
    level, text = call_tool(name, raw)
    print(f"{name}({raw})\n{level:10} | {text}\n")
