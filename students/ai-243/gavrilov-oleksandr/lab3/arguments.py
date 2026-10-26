"""Класи аргументів інструментів."""
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SearchExercisesArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(
        min_length=2,
        description="Група м'язів або рівень складності, одне-два слова українською. "
                    "Наприклад: 'спина', 'ноги', 'прес', 'початковий', 'просунутий'. "
                    "Не передавай сюди все питання користувача."
    )


class ScheduleInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    activity: str = Field(
        description="Назва заняття українською в нижньому регістрі. "
                    "Наприклад: 'йога', 'пілатес', 'силове', 'кардіо', 'розтяжка'."
    )


class CalcCaloriesArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    minutes: float = Field(gt=0, le=300, description="Тривалість тренування у хвилинах.")
    weight_kg: float = Field(gt=0, le=300, description="Вага людини в кілограмах.")
    met: float = Field(gt=0, le=20, description="Коефіцієнт навантаження MET. Якщо користувач не назвав — використовуй значення 5.")


class BookSessionArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    activity: str = Field(description="Назва заняття для запису.")
    day: str = Field(description="День тижня для запису.")


ARGS = {
    "search_exercises": SearchExercisesArgs,
    "schedule_info": ScheduleInfoArgs,
    "calc_calories": CalcCaloriesArgs,
    "book_session": BookSessionArgs,
}