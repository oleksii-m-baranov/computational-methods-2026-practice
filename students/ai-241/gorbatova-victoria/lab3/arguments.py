"""Класи аргументів інструментів для Варіанта 7 (Подорожі)."""
from pydantic import BaseModel, ConfigDict, Field

class RouteSearchArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(description="Ключове слово для пошуку маршруту українською мовою.")

class TransportInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    route: str = Field(description="Точна повна назва маршруту з довідника.")

class CalcBudgetArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    price_per_person: float = Field(gt=0, description="Вартість квитка на одну особу в грн (більше за 0).")
    people: int = Field(gt=0, description="Кількість людей у групі.")
    extra: float = Field(ge=0, description="Додаткові витрати на групу в грн.")

ARGS = {
    "search_routes": RouteSearchArgs,
    "transport_info": TransportInfoArgs,
    "calc_budget": CalcBudgetArgs,
}