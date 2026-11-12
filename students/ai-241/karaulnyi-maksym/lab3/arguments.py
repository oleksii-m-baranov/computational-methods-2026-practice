"""Класи аргументів інструментів (Варіант 1 — Бібліотека)."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class SearchBooks(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(
        description="Жанр, тема або рівень складності, одне-два слова українською, не все питання користувача цілком."
    )


class BookInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(
        description="Точна назва книжки, як вона записана в каталозі."
    )


class Calculate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation: Literal["mul", "add", "sub"] = Field(
        description="Операція: mul — множення, add — додавання, sub — віднімання."
    )
    a: float = Field(ge=0, le=10000, description="Перший операнд (невід'ємне число).")
    b: float = Field(ge=0, le=10000, description="Другий операнд (невід'ємне число).")


class IssueBook(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(description="Назва книжки для видачі.")


ARGS = {
    "search_books": SearchBooks,
    "book_info": BookInfo,
    "calculate": Calculate,
    "issue_book": IssueBook,
}
