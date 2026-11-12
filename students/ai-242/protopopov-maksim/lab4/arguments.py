"""Класи аргументів інструментів."""
from pydantic import BaseModel, ConfigDict, Field
from typing import Literal


class SearchPlantsArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(
        description=(
            "Назва рослини, умова догляду або симптом — одне-два слова "
            "українською. Не передавай усе питання користувача цілком."
        )
    )


class FertilizerInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    plant: str = Field(
        description=(
            "Точна назва рослини, записана так само, як у довіднику "
            "підживлення."
        )
    )


class CalcDoseArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pot_liters: float = Field(
        gt=0, le=100,
        description="Об'єм горщика в літрах. Не може бути від'ємним чи нульовим."
    )
    dose_ml_per_liter: float = Field(
        ge=0, le=50,
        description=(
            "Доза добрива на літр ґрунту, отримана з інструмента "
            "fertilizer_info."
        )
    )

class ConvertCurrencyArgs(BaseModel):
    amount: float = Field(..., description="Сума для конвертації")
    from_currency: Literal["USD", "EUR", "UAH"] = Field(..., description="Вхідна валюта")
    to_currency: Literal["USD", "EUR", "UAH"] = Field(..., description="Цільова валюта")

ARGS = {
    "search_plants": SearchPlantsArgs,
    "fertilizer_info": FertilizerInfoArgs,
    "calc_dose": CalcDoseArgs,
    "convert_currency": ConvertCurrencyArgs,
}