"""Класи аргументів інструментів."""
from pydantic import BaseModel, ConfigDict, Field


class SearchExercisesArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(
        min_length=2, max_length=30,
        description="Група м'язів (спина, ноги, груди, руки, прес) "
                    "або рівень складності (початковий, середній, просунутий): "
                    "одне-два слова українською в називному відмінку, "
                    "не все питання користувача цілком.",
    )


class ScheduleInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    activity: str = Field(
        min_length=2, max_length=40,
        description="Назва заняття українською в нижньому регістрі, "
                    "наприклад: йога, пілатес, силове, розтяжка, кардіо.",
    )


class CalcCaloriesArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    minutes: float = Field(gt=0, le=300, description="Тривалість тренування у хвилинах.")
    weight_kg: float = Field(ge=30, le=250, description="Вага людини в кілограмах.")
    met: float = Field(ge=1, le=20, description="Коефіцієнт навантаження MET. "
                                                "Якщо користувач його не назвав, використовуй 5.")


class BookSessionArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    activity: str = Field(description="Назва заняття")
    weekday: str = Field(description="День тижня")


class DocsArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(min_length=3, max_length=300,
                       description="Що знайти: одне-два речення українською, словами користувача")


ARGS = {
    "search_exercises": SearchExercisesArgs,
    "schedule_info": ScheduleInfoArgs,
    "calc_calories": CalcCaloriesArgs,
    "book_session": BookSessionArgs,
    "search_docs": DocsArgs,
}
