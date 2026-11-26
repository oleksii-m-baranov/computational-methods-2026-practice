"""Описи інструментів для моделі, згенеровані з класів аргументів."""
import config
from arguments import ARGS

DESCRIPTIONS = {
    "search_books": (
        "ОБОВ'ЯЗКОВО викликай першим, якщо точна назва книжки невідома. "
        "Шукає книжки за жанром, темою або рівнем складності. "
        "Повертає точні назви книжок."
    ),
    "book_info": (
        "Шукає книжку в довіднику. Використовуй ТІЛЬКИ після того, як search_books "
        "повернув точну назву книжки. НІКОЛИ не вигадуй назву самостійно!"
    ),
    "calculate": (
        "Виконує арифметичні обчислення (множення, додавання, віднімання). "
        "Використовуй ЗАВЖДИ для підрахунку штрафу (дні * штраф_за_день)."
    ),
}

SCHEMAS = []
for name in config.ALLOWED:
    SCHEMAS.append({
        "type": "function",
        "function": {
            "name": name,
            "description": DESCRIPTIONS[name],
            "parameters": ARGS[name].model_json_schema(),
        },
    })