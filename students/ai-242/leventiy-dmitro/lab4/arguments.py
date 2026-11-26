"""Класи аргументів інструментів."""
from pydantic import BaseModel, ConfigDict, Field


class SearchArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(min_length=2, description="Тема або проблема, одне-два слова українською, "
                                                 "не все питання користувача цілком")


class VaccineArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    vaccine: str = Field(description="Назва щеплення в нижньому регістрі, як вона записана в довіднику, "
                                     "наприклад: комплексне, від сказу")


class FoodArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    weight_kg: float = Field(gt=0, le=15, description="Вага кота в кілограмах")
    grams_per_kg: float = Field(gt=0, le=100, description="Норма корму в грамах на кілограм ваги на день; "
                                                          "якщо користувач не назвав, використовуй 25")
    days: float = Field(gt=0, le=365, description="На скільки днів рахуємо")


ARGS = {
    "search_articles": SearchArgs,
    "vaccine_info": VaccineArgs,
    "calc_food": FoodArgs,
}
