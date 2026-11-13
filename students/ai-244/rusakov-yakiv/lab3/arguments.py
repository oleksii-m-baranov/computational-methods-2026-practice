"""Класи аргументів інструментів."""
from pydantic import BaseModel, ConfigDict, Field


class SearchService(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(
        min_length=1,
        max_length=30,
        description="Вузол автомобіля або пробіг, одне-два слова, не все питання користувача цілком",
    )


class PriceInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")
    service: str = Field(
        min_length=1,
        description="Назва роботи в нижньому регістрі, як вона записана в прайсі",
    )


class CalcTotal(BaseModel):
    model_config = ConfigDict(extra="forbid")
    work_price: float = Field(
        gt=0, le=10000,
        description="Вартість роботи, отримана з прайсу",
    )
    part_price: float = Field(
        ge=0, le=10000,
        description="Вартість однієї деталі, отримана з прайсу",
    )
    quantity: float = Field(
        gt=0, le=100,
        description="Кількість деталей; якщо користувач не назвав, передавай 1",
    )


ARGS = {
    "search_service": SearchService,
    "price_info": PriceInfo,
    "calc_total": CalcTotal,
}
