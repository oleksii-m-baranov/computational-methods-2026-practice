"""Класи аргументів інструментів."""
from pydantic import BaseModel, ConfigDict, Field


class SearchRulesArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(min_length=1,
                       description="Тип вантажу або обмеження, одне-два слова "
                                   "українською, не все питання користувача цілком")


class TariffInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    city: str = Field(description="Назва міста українською в називному відмінку")


class CalcPriceArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    weight: float = Field(gt=0, le=1000,
                          description="Вага посилки в кілограмах")
    price_per_kg: float = Field(gt=0, le=1000,
                                description="Ціна за кілограм, отримана з довідника")
    min_price: float = Field(gt=0, le=1000,
                             description="Мінімальна вартість, отримана з довідника")


ARGS = {
    "search_rules": SearchRulesArgs,
    "tariff_info": TariffInfoArgs,
    "calc_price": CalcPriceArgs,
}
