"""Класи аргументів інструментів."""

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class SearchBooksArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(
        min_length=1,
        description="Жанр, тема або рівень складності книжки."
    )


class BookInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(
        min_length=1,
        description="Точна назва книжки з довідника."
    )


class CalculateArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    operation: Literal["mul", "add", "sub"] = Field(
        description="Операція: mul — множення, add — додавання, sub — віднімання."
    )

    a: float = Field(
        ge=0,
        description="Перше невід'ємне число."
    )

    b: float = Field(
        ge=0,
        description="Друге невід'ємне число."
    )


ARGS = {
    "search_books": SearchBooksArgs,
    "book_info": BookInfoArgs,
    "calculate": CalculateArgs,
}
