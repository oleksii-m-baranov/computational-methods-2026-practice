"""Класи аргументів інструментів для Варіанта 7 (Подорожі)."""
from pydantic import BaseModel, ConfigDict, Field


class RouteSearchArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(
        description="Ключове слово для пошуку маршруту, наприклад: 'гори', 'одеса', 'львів'."
    )


class RouteInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    route: str = Field(
        description=(
            "ТОЧНА повна назва маршруту з довідника (наприклад, 'Львів Гастрономічний' або 'Яремче'). "
            "Ніяких інших полів не передавай!"
        )
    )


class CalculateTripArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    price_per_person: float = Field(
        gt=0, description="Точна вартість квитка на одну особу з довідника (більше за 0)."
    )
    people: int = Field(gt=0, description="Кількість людей у групі.")
    extra: float = Field(ge=0, description="Додаткові витрати.")


class DocsArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(
        min_length=3,
        max_length=300,
        description="Що знайти: одне-два речення українською, словами користувача",
    )


ARGS = {
    "search_routes": RouteSearchArgs,
    "route_info": RouteInfoArgs,
    "calculate_trip": CalculateTripArgs,
    "search_docs": DocsArgs,
}