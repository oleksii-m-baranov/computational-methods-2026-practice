"""Класи аргументів інструментів (варіант 7 — Подорожі)."""
from pydantic import BaseModel, ConfigDict, Field


class SearchRoutesArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(min_length=2, max_length=30,
                       description="Тип відпочинку (природа, історія, гори, море, гастрономія) "
                                   "або назва місця: одне-два слова українською, "
                                   "не все питання користувача.")


class TransportInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    route: str = Field(min_length=2, max_length=50,
                       description="Точна назва маршруту, як вона записана в довіднику, "
                                   "у називному відмінку (наприклад, «Львів», а не «Львова»).")


class CalcBudgetArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    price_per_person: float = Field(gt=0, le=1200,
                                    description="Вартість проїзду на одну особу, грн.")
    people: int = Field(ge=1, le=50,
                        description="Кількість людей у групі.")
    extra: float = Field(ge=0, le=100000,
                         description="Додаткові витрати на всю групу, грн; якщо їх немає, передавай 0.")


class BuyTicketArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    route: str = Field(description="Назва маршруту.")


ARGS = {
    "search_routes": SearchRoutesArgs,
    "transport_info": TransportInfoArgs,
    "calc_budget": CalcBudgetArgs,
    "buy_ticket": BuyTicketArgs,
}
