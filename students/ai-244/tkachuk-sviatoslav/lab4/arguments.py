"""Pydantic-моделі аргументів для варіанта №10; ті самі параметри, що в ЛР №2."""
from pydantic import BaseModel, ConfigDict, Field

class SearchArticlesArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(min_length=1, max_length=90,
                       description="Один-два ключових слова про проблему кота українською, напр.: дряпає")

class VaccineInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    vaccine: str = Field(min_length=1, max_length=70,
                         description="Точна назва щеплення з data/vaccines.csv, напр.: комплексне")

class CalcFoodArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    weight_kg: float = Field(gt=0, le=30,
                             description="Позитивна вага кота в кг, до 30 кг включно")
    grams_per_kg: float = Field(gt=0, le=200,
                                description="Грамів корму на кг ваги на добу; за відсутності норми — 25")
    days: float = Field(gt=0, le=365,
                        description="Кількість днів для розрахунку, від 0 до 365, невключно 0")

ARGS = {
    "search_articles": SearchArticlesArgs,
    "vaccine_info": VaccineInfoArgs,
    "calc_food": CalcFoodArgs,
}
