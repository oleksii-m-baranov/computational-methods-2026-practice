"""Класи аргументів інструментів."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class SearchRoutesArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(description="Пошуковий запит для маршруту українською")


class TransportInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    route: str = Field(description="Назва маршруту")


class CalcBudgetArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    price_per_person: float = Field(gt=0, description="Ціна квитка на одну особу в один бік")
    people: float = Field(gt=0, description="Кількість людей")
    extra: float = Field(ge=0, description="Додаткові витрати")


ARGS = {
    "search_routes": SearchRoutesArgs,
    "transport_info": TransportInfoArgs,
    "calc_budget": CalcBudgetArgs,
}