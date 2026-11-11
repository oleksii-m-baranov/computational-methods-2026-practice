"""Класи аргументів інструментів."""
from pydantic import BaseModel, ConfigDict, Field

class SearchPlantsArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(description="Назва рослини, умова догляду або симптом, одне-два слова українською, не все питання користувача цілком")

class FertilizerInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    plant: str = Field(description="Точна назва рослини, як вона записана в довіднику")

class CalcDoseArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pot_liters: float = Field(gt=0, description="Об'єм горщика в літрах")
    dose_ml_per_liter: float = Field(ge=0, description="Доза на літр, отримана з довідника")

ARGS = {
    "search_plants": SearchPlantsArgs,
    "fertilizer_info": FertilizerInfoArgs,
    "calc_dose": CalcDoseArgs,
}