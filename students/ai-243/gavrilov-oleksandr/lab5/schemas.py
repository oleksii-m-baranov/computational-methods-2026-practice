"""Описи інструментів для різних конфігурацій агента."""

DESCRIPTIONS = {
    "search_docs": {
        "A": "Шукає інформацію про тренування та правила залу FitZone.",
        "B": "Шукає в документах FitZone інформацію про техніку безпеки, тренування для початківців, відновлення й харчування, абонементи, заморожування та користування обладнанням.",
        "C": "Шукає інформацію.",
    },
    "calculate": {
        "A": "Виконує базові числові обчислення.",
        "B": "Виконує точні арифметичні обчислення для числових показників.",
        "C": "Виконує арифметичну дію над двома числами.",
    },
}

RAG_DESCRIPTIONS = {
    "A": DESCRIPTIONS["search_docs"]["A"],
    "B": DESCRIPTIONS["search_docs"]["B"],
    "C": DESCRIPTIONS["search_docs"]["C"],
}

SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_docs",
            "description": DESCRIPTIONS["search_docs"]["B"],
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Пошуковий запит українською мовою",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": DESCRIPTIONS["calculate"]["B"],
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Арифметичний вираз для обчислення",
                    }
                },
                "required": ["expression"],
            },
        },
    },
]


def set_description(tool_name, desc):
    if tool_name in DESCRIPTIONS and desc in RAG_DESCRIPTIONS.values():
        for key, val in RAG_DESCRIPTIONS.items():
            if val == desc and key in DESCRIPTIONS[tool_name]:
                desc = DESCRIPTIONS[tool_name][key]
                break
    for schema in SCHEMAS:
        if isinstance(schema, dict):
            fn = schema.get("function", schema)
            if isinstance(fn, dict) and fn.get("name") == tool_name:
                fn["description"] = desc
