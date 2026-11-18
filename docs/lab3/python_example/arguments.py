from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SearchBooks(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(description="Жанр, тема або рівень складності, одне-два слова українською, не все питання користувача цілком")


class BookInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(description="Точна назва книжки, як вона записана в каталозі")


class Calculate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation: Literal['add', 'sub', 'mul'] = Field(description="add — додавання, sub — віднімання, mul — множення")
    a : float = Field(description='Перший операнд')
    b : float = Field(description='Другий операнд')


ARGS = {
    "search_books": SearchBooks,
    "book_info": BookInfo,
    'calculate': Calculate
}