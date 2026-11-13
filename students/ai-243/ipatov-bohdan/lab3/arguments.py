"""Pydantic argument schemas for library tools. Variant 11 (Library)."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class SearchBooksArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(
        min_length=2,
        max_length=50,
        description=(
            "Одне ключове слово українською: жанр або тема "
            "(наприклад 'фантастика', 'алгоритми', 'сортування'). "
            "Не передавай цілі фрази, зайві слова чи все питання користувача."
        ),
    )


class BookInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(
        min_length=2,
        max_length=100,
        description=(
            "Точна офіційна назва книжки з результату пошуку search_books "
            "(наприклад 'Основи алгоритмів', 'Зоряний експрес')."
        ),
    )


class CalculateArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    operation: Literal["mul", "add", "sub"] = Field(
        description="Арифметична дія: mul (множення), add (додавання), sub (віднімання)",
    )
    a: float = Field(
        ge=0,
        le=100000,
        description="Перше число (наприклад, кількість днів)",
    )
    b: float = Field(
        ge=0,
        le=100000,
        description="Друге число (наприклад, ставка штрафу за день)",
    )


class IssueBookArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(
        min_length=2,
        max_length=100,
        description="Назва книжки для видачі читачеві",
    )


ARGS = {
    "search_books": SearchBooksArgs,
    "book_info": BookInfoArgs,
    "calculate": CalculateArgs,
    "issue_book": IssueBookArgs,
}
