"""Pydantic-перевірка аргументів трьох інструментів."""
from pydantic import BaseModel, ConfigDict, Field


class SearchArticlesArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(min_length=1, max_length=90, description='Тема або проблема українською, одне-два ключові слова, а не все питання користувача; наприклад: дряпає.')


class VaccineInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    vaccine: str = Field(min_length=1, max_length=70, description='Назва щеплення в нижньому регістрі, як у довіднику, наприклад: комплексне.')


class CalcFoodArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    weight_kg: float = Field(gt=0, le=30, description='Вага кота у кілограмах.')
    grams_per_kg: float = Field(gt=0, le=200, description='Норма корму у грамах на кілограм ваги за день; якщо користувач не назвав норму, використовуй 25.')
    days: float = Field(gt=0, le=365, description='Тривалість розрахунку в днях.')


ARGS = {
    "search_articles": SearchArticlesArgs,
    "vaccine_info": VaccineInfoArgs,
    "calc_food": CalcFoodArgs,
}
