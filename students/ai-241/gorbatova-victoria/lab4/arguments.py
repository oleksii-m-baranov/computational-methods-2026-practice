"""Класи аргументів інструментів для Варіанта 7 (Подорожі)."""

from pydantic import BaseModel, ConfigDict, Field

class RouteSearchArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(description="Ключове слово для пошуку маршруту, наприклад: 'гори', 'одеса', 'львів'.")

class TransportInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    route: str = Field(description="ТОЧНА повна назва маршруту з довідника (наприклад, 'Кам'янець-Подільський').")

class CalcBudgetArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    price_per_person: float = Field(gt=0, description="Точна вартість квитка на одну особу з довідника (більше за 0).")
    people: int = Field(gt=0, description="Кількість людей у групі.")
    extra: float = Field(ge=0, description="Додаткові витрати.")

ARGS = {
    "search_routes": RouteSearchArgs,
    "transport_info": TransportInfoArgs,
    "calc_budget": CalcBudgetArgs,
}