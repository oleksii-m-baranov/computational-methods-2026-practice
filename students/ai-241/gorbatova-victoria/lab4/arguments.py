"""Класи аргументів інструментів для Варіанта 7 (Подорожі)."""

from pydantic import BaseModel, ConfigDict, Field


class RouteSearchArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(
        description=(
            "Тип відпочинку або назва місця, одне-два слова українською "
            "(наприклад: 'гори', 'одеса', 'львів'), не все питання користувача."
        )
    )


class TransportInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    route: str = Field(
        description=(
            "Лише один параметр route: точна назва маршруту, як записана в довіднику "
            "(наприклад: 'Кам'янець-Подільський'). Без полів from, to, people, price_per_person."
        )
    )


class CalcBudgetArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    price_per_person: float = Field(
        gt=0,
        description="Вартість проїзду на одну особу з довідника (число більше 0).",
    )
    people: int = Field(
        gt=0,
        description="Кількість людей у групі (ціле число більше 0).",
    )
    extra: float = Field(
        ge=0,
        description="Додаткові витрати на всю групу; якщо їх немає, передавай 0.",
    )


ARGS = {
    "search_routes": RouteSearchArgs,
    "transport_info": TransportInfoArgs,
    "calc_budget": CalcBudgetArgs,
}