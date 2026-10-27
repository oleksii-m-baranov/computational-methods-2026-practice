"""Pydantic-моделі аргументів інструментів."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SearchBooksArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(
        min_length=1,
        max_length=100,
        description="Ключове слово для пошуку книжок",
    )


class BookInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(
        min_length=1,
        description="Точна назва книжки в каталозі",
    )


class CalculateArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    operation: Literal["add", "sub", "mul"] = Field(
        description="Арифметична операція",
    )

    a: float = Field(
        ge=-1000000,
        le=1000000,
        description="Перший операнд",
    )

    b: float = Field(
        ge=-1000000,
        le=1000000,
        description="Другий операнд",
    )
ARGS = {
    "search_books": SearchBooksArgs,
    "book_info": BookInfoArgs,
    "calculate": CalculateArgs,
}