"""Класи аргументів інструментів (Варіант 1 — Бібліотека)."""
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SearchBooksArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(
        description=(
            "Назва книжки, жанр, тема або рівень складності (1-3 слова українською). "
            "НЕ передавай усе питання користувача цілком."
        )
    )


class BookInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(
        description="Точна назва книжки, як вона записана в каталозі."
    )


class CalculateArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation: Literal["mul", "add", "sub"] = Field(
        description="Арифметична операція: mul — множення, add — додавання, sub — віднімання."
    )
    a: float = Field(ge=0, le=10000, description="Перший операнд.")
    b: float = Field(ge=0, le=10000, description="Другий операнд.")


ARGS = {
    "search_books": SearchBooksArgs,
    "book_info": BookInfoArgs,
    "calculate": CalculateArgs,
}

