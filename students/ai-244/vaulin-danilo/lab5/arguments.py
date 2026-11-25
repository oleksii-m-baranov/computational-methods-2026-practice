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


class DocsArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(min_length=3, max_length=300,
                       description="Що знайти: одне-два речення українською, словами користувача")


ARGS = {
    "search_books": SearchBooksArgs,
    "book_info": BookInfoArgs,
    "calculate": CalculateArgs,
    "search_docs": DocsArgs,
}

