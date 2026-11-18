from dispatcher import call_tool

cases = [
    ("search_recipes", '{"query": "рис"'),                                      # зламаний JSON
    ("search_recipes", '{"query": []}'),                                        # неправильний тип
    ("search_recipes", '{}'),                                                   # немає поля
    ("search_recipes", '{"query": "рис", "x": 1}'),                              # вигадане поле
    ("unknown_tool", '{}'),                                                     # неіснуючий інструмент
    ("place_order", '{}'),                                                      # заборонена дія
    ("product_info", '{"product": "__невідомий_продукт__"}'),                   # значення немає в довіднику
    ("scale_amount", '{"amount": 0, "base_servings": 2, "target_servings": 4}'), # значення поза межами
]

for name, raw in cases:
    level, text = call_tool(name, raw)
    print(f"{level:10} | {text}\n")
