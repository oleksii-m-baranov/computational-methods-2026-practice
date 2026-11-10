"""Класи аргументів інструментів."""
from pydantic import BaseModel, ConfigDict, Field


class SearchWorksArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(description="Тип роботи або категорія, одне-два слова українською "
                                   "у називному відмінку, наприклад: стеля, ламінат, "
                                   "сантехніка. Не передавай усе питання користувача цілком.")


class MaterialInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    material: str = Field(description="Назва матеріалу в нижньому регістрі, як вона записана "
                                      "в довіднику, наприклад: ґрунтовка, ламінат.")


class CalcMaterialsArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    area: float = Field(gt=0, le=500, description="Площа в квадратних метрах")
    coverage_m2: float = Field(gt=0, description="Покриття однієї одиниці в м², отримане з довідника")
    price: float = Field(gt=0, description="Ціна за одиницю в гривнях, отримана з довідника")


ARGS = {
    "search_works": SearchWorksArgs,
    "material_info": MaterialInfoArgs,
    "calc_materials": CalcMaterialsArgs,
}
