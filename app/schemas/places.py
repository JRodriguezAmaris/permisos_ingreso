"""Esquemas para las sucursales y estaciones."""
from pydantic import BaseModel


class DepartmentSchema(BaseModel):
    """Esquema de departamentos."""
    id: int
    name: str
    cod_dane: str

    class Config:
        from_attributes = True


class MunicipalitySchema(BaseModel):
    """Esquema de municipios."""
    id: int
    name: str
    cod_dane: str
    department_id: int

    class Config:
        from_attributes = True


class CitySchema(BaseModel):
    """Esquema de ciudades."""
    id: int
    name: str
    municipality_id: int

    class Config:
        from_attributes = True
