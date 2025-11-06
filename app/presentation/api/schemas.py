from typing import (
    Any,
    Generic,
    TypeVar,
)

from pydantic import (
    BaseModel,
    Field,
)

from presentation.api.filters import PaginationOut


TData = TypeVar("TData")
TListItem = TypeVar("TListItem")


class PingResponseSchema(BaseModel):
    result: bool


class ListPaginatedResponse(BaseModel, Generic[TListItem]):
    items: list[TListItem]
    pagination: PaginationOut


class ApiResponse(BaseModel, Generic[TData]):
    data: TData | dict = Field(default_factory=dict)
    meta: dict[str, Any] = Field(default_factory=dict)
    errors: list[Any] = Field(default_factory=list)


class ErrorSchema(BaseModel):
    """Схема для ошибок в API."""

    data: dict = Field(default_factory=dict)
    meta: dict[str, Any] = Field(default_factory=dict)
    errors: list[dict[str, str]] = Field(
        default_factory=list,
        description="Список ошибок с полем message",
    )
