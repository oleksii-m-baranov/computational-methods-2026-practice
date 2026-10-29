"""Класи аргументів інструментів."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class SearchExercises(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(
        min_length=1,
        description="Група м'язів або рівень складності, одне-два слова українською, "
                    "не все питання користувача цілком",
    )

class ScheduleInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")
    activity: str = Field(
        min_length=1,
        description="Назва заняття українською в нижньому регістрі",
    )

class CalcCalories(BaseModel):
    model_config = ConfigDict(extra="forbid")
    minutes: float = Field(gt=0, le=300, description="Тривалість тренування у хвилинах")
    weight_kg: float = Field(gt=20, le=300, description="Вага людини в кілограмах")
    met: float = Field(gt=0, le=20,
                       description="Коефіцієнт навантаження; якщо користувач його не назвав, використовуй 5")

ARGS = {
    "search_exercises": SearchExercises,
    "schedule_info": ScheduleInfo,
    "calc_calories": CalcCalories,
}