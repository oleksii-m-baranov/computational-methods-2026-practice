"""Класи аргументів інструментів (Варіант 1: Бібліотека)."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class SearchBooksArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(
        min_length=1,
        description=(
            "Передавай strictly ОДНЕ слово українською: "
            "або жанр ('фантастика'), або тему ('алгоритми'), "
            "або складність ('легкий'). Ніколи не об'єднуй кілька слів! "
            "Передавай корінь одного слова українською (наприклад: 'алгоритм', 'фантаст', 'легк'). Не додавай закінчень!"
        ),
    )


class DocsArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(
        min_length=3,
        max_length=300,
        description="Що знайти: одне-два речення українською, словами користувача",
    )


class BookInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(
        min_length=1,
        description="Точна назва книжки, яка була отримана з search_books",
    )


class CalculateArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation: Literal["mul", "add", "sub"] = Field(
        description="mul — множення, add — додавання, sub — віднімання"
    )
    a: float = Field(
        gt=0,
        le=100000,
        description="Перше додатне число (наприклад, кількість днів)",
    )
    b: float = Field(
        gt=0,
        le=100000,
        description="Друге додатне число (наприклад, ставка штрафу)",
    )


ARGS = {
    "search_books": SearchBooksArgs,
    "search_docs": DocsArgs,
    "book_info": BookInfoArgs,
    "calculate": CalculateArgs,
}