"""Rutas para manejar las sedes de la aplicación."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional

from app.db.database import get_db
from app.models.branches import Branch, BranchTypes
from app.schemas.branches import BranchSchema
from app.utils.pagination import paginate, PaginatedResponse

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[BranchSchema])
def get_branches(
    branch_type: Optional[BranchTypes] = Query(None, description="Filtrar por tipo de sede"),
    search: Optional[str] = Query(None, description="Buscar por nombre o dirección"),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, le=100),
    db: Session = Depends(get_db),
):
    """Obtiene una lista de sedes, opcionalmente filtradas por tipo, nombre o dirección."""
    query = db.query(Branch)
    if branch_type:
        query = query.filter(Branch.type == branch_type)
    if search:
        # Búsqueda parcial por nombre o dirección, insensible a mayúsculas
        search = f"%{search.lower()}%"
        query = query.filter(
            or_(
                Branch.name.ilike(search),
                Branch.address.ilike(search)
            )
        )
    return paginate(query, BranchSchema, offset=offset, limit=limit)
