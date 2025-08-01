"""Modulo de paginacion."""
from typing import List, TypeVar, Generic, Type
from pydantic import BaseModel
from sqlalchemy.orm import Query

from app.config.settings import settings

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Esquema para paginación."""
    total: int
    items: List[T]
    offset: int
    limit: int


def paginate(query: Query, model: Type[T], offset: int = settings.PAGE_OFFSET, limit: int = settings.PAGE_OFFSET) -> PaginatedResponse[T]:
    """Genera una respuesta paginada y hace la paginación a nivel de query."""
    total = query.count()
    items = query.offset(offset).limit(limit).all()
    return PaginatedResponse[T](
        total=total,
        items=items,
        offset=offset,
        limit=limit
    )
