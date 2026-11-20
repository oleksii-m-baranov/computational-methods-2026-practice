"""Описи інструментів для моделі, згенеровані з класів аргументів."""
from pydantic import BaseModel, ConfigDict, Field
import config


# 1. Класи аргументів (варіант із model_json_schema)
class SearchRoutesArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(description="Тип відпочинку або назва місця, одне-два слова українською, не все питання користувача")


class DocsArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(
        min_length=3,
        max_length=300,
        description="Що знайти: одне-два речення українською, словами користувача",
    )


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
    "search_docs": DocsArgs,
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

RAG_DESCRIPTIONS = {
    "A": "Шукає маршрути вихідного дня за типом відпочинку або назвою місця. "
         "Використовуй, коли користувач описує, куди або як хоче поїхати.",
    "B": (
        "ЄДИНЕ джерело офіційних правил, регламентів і тарифних умов по документах бази знань "
        "(зокрема туристичного центру «Азимут-Південь»: перевезення багажу та ручної поклажі, "
        "вага/обсяг, доплати, спортивний інвентар, рідини та заборонені предмети, бирки, зберігання, "
        "акти пошкодження/втрати та інші внутрішні положення). "
        "Викликай ЗАВЖДИ, коли питання стосується правил, норм, лімітів, доплат, термінів або "
        "умов з регламентів — не вигадуй і не відповідай з пам'яті, бо точні цифри та правила "
        "є лише в документах. Якщо інструмент повернув, що нічого не знайдено, так і скажи користувачу "
        "та не вигадуй відповідь."
    ),
    "C": "Шукає інформацію.",
}

DESCRIPTIONS["search_docs"] = RAG_DESCRIPTIONS[getattr(config, "DOCS_DESCRIPTION", "B")]


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


def set_description(name, text):
    """Підміняє опис інструмента в SCHEMAS: це той самий список, який читає agent.py."""
    for item in SCHEMAS:
        if item["function"]["name"] == name:
            item["function"]["description"] = text