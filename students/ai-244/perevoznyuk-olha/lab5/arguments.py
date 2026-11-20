from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

class search_routes(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(
        description="тип відпочинку або назва місця, одне-два слова українською, не все питання користувача"
    )

class transport_info(BaseModel):
    model_config = ConfigDict(extra="forbid")
    route: str = Field(
        description="точна назва маршруту, як вона записана в довіднику"
    )

class calc_budget(BaseModel):
    model_config = ConfigDict(extra="forbid")
    price_per_person: float = Field(
        description="Вартість проїзду на одну особу"
    )
    people: int = Field(
        description="Кількість людей у групі"
    )
    extra: float = Field(
        description="Додаткові витрати на групу (наприклад, оренда транспорту)"
    )

class DocsArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(min_length=3, max_length=300,
                       description="Що знайти: одне-два речення українською, словами користувача")

ARGS = {
    "search_routes": search_routes,
    "transport_info": transport_info,
    "calc_budget": calc_budget,
    "search_docs": DocsArgs,
}