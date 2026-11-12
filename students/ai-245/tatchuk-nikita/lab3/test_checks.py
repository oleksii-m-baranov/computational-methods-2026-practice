from dispatcher import call_tool

cases = [
    ("calc_materials", '{"area": 18, "coverage_m2": 5, "price": 450'),               # зламаний JSON
    ("calc_materials", '{"area": "вісімнадцять", "coverage_m2": 5, "price": 450}'),  # неправильний тип
    ("calc_materials", '{"area": 18, "coverage_m2": 5}'),                            # немає поля
    ("material_info", '{"material": "шпалери", "unit": "рулон"}'),                   # вигадане поле
    ("delete_all", '{}'),                                                            # неіснуючий інструмент
    ("place_order", '{"material": "шпалери", "quantity": 4}'),                       # заборонена дія
    ("material_info", '{"material": "демпферна стрічка"}'),                          # немає в довіднику
    ("calc_materials", '{"area": 18, "coverage_m2": 0, "price": 0}'),                # поза межами
    ("calc_materials", '{"area": 18, "coverage_m2": 20, "price": 450}'),             # покриття й ціна з різних матеріалів
]

for name, raw in cases:
    level, text = call_tool(name, raw)
    print(f"{level:10} | {text}\n")
