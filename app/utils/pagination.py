"""Modulo de paginacion."""
from typing import List, Optional, TypeVar, Generic, Type
from pydantic import BaseModel
from sqlalchemy.orm import Query

from app.config.settings import settings

T = TypeVar("T")
S = TypeVar("S", bound=BaseModel)


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

class PaginatedModelResponse(BaseModel, Generic[S]):
    """Esquema para paginación."""
    total: int
    items: List[S]
    offset: int
    limit: int


def paginate_model(
    query: Query,
    schema: Optional[Type[S]] = None,
    offset: int = settings.PAGE_OFFSET,
    limit: int = settings.PAGE_LIMIT,
) -> PaginatedResponse[S] | PaginatedResponse[T]:
    """Genera una respuesta paginada opcionalmente transformando a un esquema Pydantic."""
    total = query.count()
    items = query.offset(offset).limit(limit).all()

    if schema:
        items = [schema.model_validate(item) for item in items]

    return PaginatedResponse[S](
        total=total,
        items=items,
        offset=offset,
        limit=limit
    )
