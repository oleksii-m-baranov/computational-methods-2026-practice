"""Класи аргументів інструментів."""
from pydantic import BaseModel, ConfigDict, Field


class SearchExercisesArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(
        min_length=1,
        description="Група м'язів (спина, ноги, груди, руки, прес) "
                    "або рівень складності (початковий, середній, просунутий): "
                    "одне-два слова українською, не все питання користувача цілком.",
    )


class ScheduleInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    activity: str = Field(
        min_length=1,
        description="Назва заняття українською в нижньому регістрі (наприклад, «йога», «силове»).",
    )


class CalcCaloriesArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    minutes: float = Field(
        gt=0,
        le=600,
        description="Тривалість тренування у хвилинах.",
    )
    weight_kg: float = Field(
        gt=20,
        le=300,
        description="Вага людини в кілограмах.",
    )
    met: float = Field(
        gt=0,
        le=25,
        description="Коефіцієнт навантаження; якщо користувач його не назвав, використовуй 5.",
    )


ARGS = {
    "search_exercises": SearchExercisesArgs,
    "schedule_info": ScheduleInfoArgs,
    "calc_calories": CalcCaloriesArgs,
}

class DocsArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(min_length=3, max_length=300,
                       description="Що знайти: одне-два речення українською, словами користувача")


ARGS["search_docs"] = DocsArgs
