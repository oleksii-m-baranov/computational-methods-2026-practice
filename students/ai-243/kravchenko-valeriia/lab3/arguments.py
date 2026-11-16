"""Класи аргументів інструментів (Pydantic)."""
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SearchRulesArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(
        min_length=2,
        max_length=50,
        description=(
            "Тип вантажу або обмеження, одне-два слова українською. "
            "Не передавай усе питання користувача цілком."
        ),
    )


class TariffInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    city: str = Field(
        min_length=2,
        max_length=50,
        description="Назва міста українською в називному відмінку.",
    )


class CalcPriceArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    weight: float = Field(
        gt=0, le=30,
        description="Вага посилки в кілограмах (більше 0 і не більше 30).",
    )
    price_per_kg: float = Field(
        gt=0, le=1000,
        description="Ціна за кілограм, отримана з довідника.",
    )
    min_price: float = Field(
        ge=0, le=10000,
        description="Мінімальна вартість, отримана з довідника.",
    )


ARGS = {
    "search_rules": SearchRulesArgs,
    "tariff_info":  TariffInfoArgs,
    "calc_price":   CalcPriceArgs,
}
