"""Описи інструментів для моделі, згенеровані з класів аргументів."""
from pydantic import BaseModel, ConfigDict, Field
import config


# 1. Класи аргументів (варіант із model_json_schema)
class SearchRoutesArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(description="Тип відпочинку або назва місця, одне-два слова українською, не все питання користувача")


class TransportInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    route: str = Field(description="Точна назва маршруту, як вона записана в довіднику")


class CalcBudgetArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    price_per_person: float = Field(gt=0, description="Вартість проїзду на одну особу")
    people: float = Field(gt=0, description="Кількість людей у групі")
    extra: float = Field(ge=0, description="Додаткові витрати на всю групу; якщо їх немає, передавай 0")


ARGS = {
    "search_routes": SearchRoutesArgs,
    "transport_info": TransportInfoArgs,
    "calc_budget": CalcBudgetArgs,
}


# 2. Описи інструментів
DESCRIPTIONS = {
    "search_routes": "Шукає маршрути вихідного дня за типом відпочинку або назвою місця. "
                     "Використовуй, коли користувач описує, куди або як хоче поїхати.",
    "transport_info": "Шукає маршрут у довіднику транспорту, повертає вартість проїзду на одну особу, час у дорозі "
                      "та кількість рейсів на день. Використовуй, коли маршрут уже обрано.",
    "calc_budget": "Обчислює загальний бюджет поїздки на групу у гривнях. "
                   "Використовуй ЗАВЖДИ, коли треба порахувати бюджет; самостійно модель не рахує.",
}


# 3. Автоматична генерація списку SCHEMAS на основі config.ALLOWED
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