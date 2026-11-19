from dispatcher import call_tool

cases = [
    ("scale_amount", '{"amount": 300, "base_servings": 4, "target_servings": 10'),             # зламаний JSON
    ("scale_amount", '{"amount": "триста", "base_servings": 4, "target_servings": 10}'),       # неправильний тип
    ("scale_amount", '{"amount": 300, "base_servings": 4}'),                                   # немає поля
    ("scale_amount", '{"amount": 300, "base_servings": 4, "target_servings": 10, "x": 1}'),    # вигадане поле
    ("delete_all", '{}'),                                                                      # неіснуючий інструмент
    ("place_order", '{"product": "рис"}'),                                                     # заборонена дія
    ("product_info", '{"product": "маскарпоне"}'),                                             # значення немає в довіднику
    ("scale_amount", '{"amount": 300, "base_servings": 0, "target_servings": 10}'),            # значення поза межами
    # додатково
    ("product_info", '{"product": "рису"}'),                                                   # відмінок -> підказка
    ("search_recipes", '{"query": ""}'),                                                       # порожній запит
    ("product_info", '{"product": "рис"}'),                                                    # все гаразд
]

for name, raw in cases:
    level, text = call_tool(name, raw)
    print(f"{level:10} | {text}\n")
