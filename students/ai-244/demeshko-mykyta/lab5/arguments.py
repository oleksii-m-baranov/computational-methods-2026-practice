"""Класи аргументів інструментів."""
from pydantic import BaseModel, ConfigDict, Field


class SearchPlantsArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(
        min_length=1,
        max_length=100,
        description=(
            "Назва рослини, умова догляду або симптом, одне-два слова українською, "
            "не все питання користувача цілком"
        ),
    )


class FertilizerInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    plant: str = Field(
        min_length=1,
        max_length=100,
        description="Точна назва рослини, як вона записана в довіднику",
    )


class CalcDoseArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pot_liters: float = Field(
        gt=0,
        le=200,
        description="Об'єм горщика в літрах (більше 0, до 200)",
    )
    dose_ml_per_liter: float = Field(
        gt=0,
        le=100,
        description="Доза на літр, отримана з довідника (більше 0, до 100)",
    )


class DocsArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(
        min_length=3,
        max_length=300,
        description="Що знайти: одне-два речення українською, словами користувача",
    )


ARGS = {
    "search_plants": SearchPlantsArgs,
    "fertilizer_info": FertilizerInfoArgs,
    "calc_dose": CalcDoseArgs,
    "search_docs": DocsArgs,
}