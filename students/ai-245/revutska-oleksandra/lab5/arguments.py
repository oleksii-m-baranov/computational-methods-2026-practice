
"""Pydantic-моделі аргументів інструментів бібліотечного агента."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SearchBooksArgs(BaseModel):
    """Аргументи пошуку книжок."""

    model_config = ConfigDict(extra="forbid")

    query: str = Field(
        min_length=1,
        max_length=100,
        description="Ключове слово або короткий запит для пошуку книжок",
    )


class BookInfoArgs(BaseModel):
    """Аргументи отримання інформації про книжку."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(
        min_length=1,
        description="Точна назва книжки в каталозі",
    )


class CalculateArgs(BaseModel):
    """Аргументи арифметичних обчислень."""

    model_config = ConfigDict(extra="forbid")

    operation: Literal["add", "sub", "mul"] = Field(
        description="Арифметична операція: додавання, віднімання або множення",
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


class SearchDocsArgs(BaseModel):
    """Аргументи семантичного пошуку в документах через RAG."""

    model_config = ConfigDict(extra="forbid")

    query: str = Field(
        min_length=1,
        max_length=500,
        description=(
            "Запитання українською мовою для семантичного "
            "пошуку інформації в документах бібліотеки"
        ),
    )


# Реєстр моделей аргументів інструментів
ARGS = {
    "search_books": SearchBooksArgs,
    "book_info": BookInfoArgs,
    "calculate": CalculateArgs,
    "search_docs": SearchDocsArgs,
}
