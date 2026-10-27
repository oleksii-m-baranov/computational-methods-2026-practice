"""Pydantic argument schemas for library tools. Variant 11 (Library)."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class SearchBooksArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(
        min_length=2,
        max_length=50,
        description=(
            "Жанр, тема або рівень складності книжки, одне-два слова українською "
            "(наприклад 'фантастика', 'алгоритми', 'сортування'). "
            "Не передавай усе питання користувача цілком."
        ),
    )


class BookInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(
        min_length=2,
        max_length=100,
        description=(
            "Точна офіційна назва книжки з каталогу (наприклад 'Основи алгоритмів', 'Зоряний експрес'). "
            "Використовуй лише після того, як назву знайдено через search_books. "
            "Не вигадуй назви самостійно."
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
        description="Перше число, невід'ємне (наприклад, кількість днів прострочення)",
    )
    b: float = Field(
        ge=0,
        le=100000,
        description="Друге число, невід'ємне (наприклад, ставка штрафу за день у гривнях)",
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
