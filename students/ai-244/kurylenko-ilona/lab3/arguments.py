"""Класи аргументів інструментів."""

from pydantic import BaseModel, ConfigDict, Field


class SearchArticlesArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(
        description="Тема або проблема догляду за котом, "
                    "одне-два слова українською, "
                    "не все питання користувача цілком"
    )


class VaccineInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    vaccine: str = Field(
        description="Точна назва щеплення в нижньому регістрі, "
                    "як вона записана в довіднику vaccines.csv"
    )


class CalcFoodArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    weight_kg: float = Field(
        gt=0,
        le=20,
        description="Вага кота в кілограмах, більше 0 "
                    "і не більше 20. Якщо вага вказана "
                    "у грамах, переведи її у кілограми"
    )

    grams_per_kg: float = Field(
        gt=0,
        le=1000,
        description="Норма корму в грамах на кілограм "
                    "ваги за день. Якщо користувач "
                    "не вказав норму, передай 25"
    )

    days: float = Field(
        gt=0,
        le=365,
        description="Кількість днів, на які "
                    "розраховується корм"
    )


ARGS = {
    "search_articles": SearchArticlesArgs,
    "vaccine_info": VaccineInfoArgs,
    "calc_food": CalcFoodArgs,
}
