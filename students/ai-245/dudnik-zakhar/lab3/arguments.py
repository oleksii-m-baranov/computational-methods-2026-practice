from pydantic import BaseModel, ConfigDict, Field


class search_exercises(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(description="Група м'язів або рівень складності, "
                                       "одне-два слова українською, "
                                       "не все питання користувача цілком")


class schedule_info(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(description="Назва заняття українською в нижньому регістрі")


class calc_calories(BaseModel):
    model_config = ConfigDict(extra="forbid")
    minutes : float = Field(gt=0, description='Тривалість тренування у хвилинах')
    weight_kg : float = Field(gt=0, lt=250, description='вага людини в кілограмах')
    met : float = Field(description='коефіцієнт навантаження; якщо користувач його не назвав, використовуй 5')


ARGS = {
    "search_exercises": search_exercises,
    "schedule_info": schedule_info,
    'calc_calories': calc_calories
}
