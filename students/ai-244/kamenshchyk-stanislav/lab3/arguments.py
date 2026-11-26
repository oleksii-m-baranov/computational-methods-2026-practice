"""Класи аргументів інструментів для варіанта 8 (автосервіс)."""
from pydantic import BaseModel, ConfigDict, Field


class SearchServiceArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(
        min_length=1,
        max_length=40,
        description=(
            "Вузол автомобіля або пробіг (одне-два слова українською, "
            "наприклад: 'гальма', 'двигун', 'підвіска', '30'). "
            "Не передавай усе питання користувача цілком."
        ),
    )


class PriceInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    service: str = Field(
        min_length=1,
        max_length=80,
        description="Точна назва регламентної роботи в нижньому регістрі, як вона записана в прайсі.",
    )


class CalcTotalArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    work_price: float = Field(
        gt=0,
        le=50000,
        description="Вартість роботи в гривнях, отримана з прайсу через price_info.",
    )
    part_price: float = Field(
        ge=0,
        le=100000,
        description="Вартість однієї деталі в гривнях, отримана з прайсу через price_info (може бути 0, якщо деталі не потрібні).",
    )
    quantity: float = Field(
        gt=0,
        le=100,
        description="Кількість деталей; якщо користувач не назвав конкретну кількість, передавай 1.",
    )


ARGS = {
    "search_service": SearchServiceArgs,
    "price_info": PriceInfoArgs,
    "calc_total": CalcTotalArgs,
}
