"""Класи аргументів інструментів (варіант 1 — Бібліотека)."""
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SearchBooksArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(
        min_length=1,
        max_length=100,
        description="Жанр, тема або рівень складності, одне-два слова "
                     "українською, не все питання користувача цілком",
    )


class BookInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(
        min_length=1,
        max_length=200,
        description="Точна назва книжки, як вона записана в каталозі",
    )


class CalculateArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation: Literal["mul", "add", "sub"] = Field(
        description="mul — множення, add — додавання, sub — віднімання",
    )
    a: float = Field(ge=0, le=100000, description="Перший операнд")
    b: float = Field(ge=0, le=100000, description="Другий операнд")


ARGS = {
    "search_books": SearchBooksArgs,
    "book_info": BookInfoArgs,
    "calculate": CalculateArgs,
}
