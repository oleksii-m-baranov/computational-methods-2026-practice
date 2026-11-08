"""Класи аргументів інструментів."""
from pydantic import BaseModel, ConfigDict, Field


class SearchRoutesArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(
        min_length=1, max_length=40,
        description="Тип відпочинку або назва місця: одне-два слова українською "
                    "(наприклад, «гори» або «море»), не все питання користувача.")


class TransportInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    route: str = Field(
        description="Точна назва маршруту в називному відмінку, як вона записана "
                    "в довіднику. Якщо не знаєш точної назви, спершу знайди її "
                    "інструментом search_routes.")


class CalcBudgetArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    price_per_person: float = Field(
        gt=0, le=5000,
        description="Вартість проїзду на одну особу, грн.")
    people: int = Field(
        ge=1, le=50,
        description="Кількість людей у групі.")
    extra: float = Field(
        ge=0, le=100000,
        description="Додаткові витрати на всю групу, грн; "
                    "якщо їх немає, передавай 0.")


ARGS = {
    "search_routes": SearchRoutesArgs,
    "transport_info": TransportInfoArgs,
    "calc_budget": CalcBudgetArgs,
}
