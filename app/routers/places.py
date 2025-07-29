"""Rutas para manejar las referencias a lugares de la aplicación."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.models.places import Department, Municipality, City
from app.schemas.places import DepartmentSchema, MunicipalitySchema, CitySchema
from app.utils.pagination import paginate, PaginatedResponse

router = APIRouter()


@router.get("/departments", response_model=PaginatedResponse[DepartmentSchema])
def get_departments(
    name: Optional[str] = Query(None, description="Buscar por departamento"),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, le=100),
    db: Session = Depends(get_db),
):
    """Obtiene una lista de departamentos, opcionalmente filtradas por nombre."""
    query = db.query(Department)
    if name:
        # Búsqueda parcial por nombre insensible a mayúsculas
        query = query.filter(Department.name.ilike(f"%{name.lower()}%"))
    return paginate(query, DepartmentSchema, offset=offset, limit=limit)


@router.get("/municipalities", response_model=PaginatedResponse[MunicipalitySchema])
def get_municipalities(
    name: Optional[str] = Query(None, description="Buscar por municipio"),
    department_id: Optional[int] = Query(None, description="Buscar por departamento"),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, le=100),
    db: Session = Depends(get_db),
):
    """Obtiene una lista de municipios, opcionalmente filtradas por nombre."""
    query = db.query(Municipality)
    if name:
        # Búsqueda parcial por nombre insensible a mayúsculas
        query = query.filter(Municipality.name.ilike(f"%{name.lower()}%"))
    if department_id:
        query = query.filter(Municipality.department_id == department_id)
    return paginate(query, MunicipalitySchema, offset=offset, limit=limit)


@router.get("/cities", response_model=PaginatedResponse[CitySchema])
def get_cities(
    name: Optional[str] = Query(None, description="Buscar por ciudad"),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, le=100),
    db: Session = Depends(get_db),
):
    """Obtiene una lista de ciudades, opcionalmente filtradas por nombre."""
    query = db.query(City)
    if name:
        # Búsqueda parcial por nombre insensible a mayúsculas
        query = query.filter(City.name.ilike(f"%{name.lower()}%"))
    return paginate(query, CitySchema, offset=offset, limit=limit)
