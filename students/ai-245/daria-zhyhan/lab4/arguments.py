"""Класи аргументів інструментів."""

from pydantic import BaseModel, ConfigDict, Field


class SearchPlantsArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(
        min_length=2,
        max_length=50,
        description="Назва рослини, умова догляду або симптом, одне-два слова українською, не все питання користувача цілком",
    )


class FertilizerInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    plant: str = Field(
        min_length=2,
        max_length=50,
        description="Точна назва рослини, як вона записана в довіднику",
    )


class CalcDoseArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pot_liters: float = Field(
        gt=0,
        le=100,
        description="Об'єм горщика в літрах (додатне число більше 0 і не більше 100)",
    )
    dose_ml_per_liter: float = Field(
        ge=0,
        le=50,
        description="Доза на літр у мілілітрах, отримана з довідника (від 0 до 50)",
    )


ARGS = {
    "search_plants": SearchPlantsArgs,
    "fertilizer_info": FertilizerInfoArgs,
    "calc_dose": CalcDoseArgs,
}