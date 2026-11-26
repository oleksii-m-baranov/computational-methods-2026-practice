"""Класи аргументів інструментів."""
from pydantic import BaseModel, ConfigDict, Field


class SearchExercisesArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(
        min_length=1,
        description="Група м'язів або рівень складності, одне-два слова українською "
                    "в називному відмінку (наприклад: спина, ноги, початковий). "
                    "Не передавай все питання користувача цілком.",
    )


class ScheduleInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    activity: str = Field(
        min_length=1,
        description="Назва заняття українською в нижньому регістрі (наприклад: йога).",
    )


class CalcCaloriesArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    minutes: float = Field(gt=0, le=480, description="Тривалість тренування у хвилинах")
    weight_kg: float = Field(ge=30, le=300, description="Вага людини в кілограмах")
    met: float = Field(ge=1, le=20,
                       description="Коефіцієнт навантаження. Якщо користувач його "
                                   "не назвав, використовуй 5")


ARGS = {
    "search_exercises": SearchExercisesArgs,
    "schedule_info": ScheduleInfoArgs,
    "calc_calories": CalcCaloriesArgs,
}
