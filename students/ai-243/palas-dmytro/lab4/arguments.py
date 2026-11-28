"""Класи аргументів інструментів (Варіант 16 — Ремонт квартири)."""
from pydantic import BaseModel, ConfigDict, Field


class SearchWorksArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(
        min_length=1,
        max_length=100,
        description="Тип роботи або категорія, одне-два слова українською, не все питання користувача цілком",
    )


class MaterialInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    material: str = Field(
        min_length=1,
        max_length=100,
        description="Назва матеріалу в нижньому регістрі, як вона записана в довіднику",
    )


class CalcMaterialsArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    area: float = Field(gt=0, le=10000, description="Площа в квадратних метрах")
    coverage_m2: float = Field(gt=0, le=1000, description="Покриття однієї одиниці, отримане з довідника")
    price: float = Field(gt=0, le=100000, description="Ціна за одиницю, отримана з довідника")


ARGS = {
    "search_works": SearchWorksArgs,
    "material_info": MaterialInfoArgs,
    "calc_materials": CalcMaterialsArgs,
}
