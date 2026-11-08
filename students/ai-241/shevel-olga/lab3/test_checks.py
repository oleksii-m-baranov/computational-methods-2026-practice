from dispatcher import call_tool

cases = [
    ("calc_price", '{"weight": 15, "price_per_kg": 18, "min_price": 70'),            # зламаний JSON
    ("calc_price", '{"weight": "сто", "price_per_kg": 18, "min_price": 70}'),        # неправильний тип
    ("calc_price", '{"weight": 15}'),                                                # немає поля
    ("tariff_info", '{"city": "Львів", "x": 1}'),                                    # вигадане поле
    ("delete_all", '{}'),                                                            # неіснуючий інструмент
    ("cancel_parcel", '{"parcel_id": "123"}'),                                       # заборонена дія
    ("tariff_info", '{"city": "Львов"}'),                                            # немає в довіднику
    ("calc_price", '{"weight": -5, "price_per_kg": 18, "min_price": 70}'),           # поза межами
    ("calc_price", '{"weight": 15, "price_per_kg": 10.5, "min_price": 20}'),         # вигадана пара з Z3
    ("tariff_info", '{"city": "Львів"}'),                                            # усе гаразд
]

for name, raw in cases:
    level, text = call_tool(name, raw)
    print(f"{level:10} | {text}\n")
