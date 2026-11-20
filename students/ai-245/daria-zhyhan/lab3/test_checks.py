"""Перевірка ланцюжка перевірок диспетчера без виклику моделі."""

from dispatcher import call_tool

cases = [
    ("calc_dose", '{"pot_liters": 3, "dose_ml_per_liter": 5'),          
    ("calc_dose", '{"pot_liters": "три", "dose_ml_per_liter": 5}'),        
    ("calc_dose", '{"pot_liters": 3}'),                                 
    ("calc_dose", '{"pot_liters": 3, "dose_ml_per_liter": 5, "x": 1}'),  
    ("delete_all", '{}'),                                                 
    ("order_fertilizer", '{"plant": "Фікус", "amount_ml": 15}'),        
    ("fertilizer_info", '{"plant": "Кактус сагуаро"}'),                   
    ("calc_dose", '{"pot_liters": -2, "dose_ml_per_liter": 5}'),         
]

for name, raw in cases:
    level, text = call_tool(name, raw)
    print(f"{level:10} | {text}\n")
