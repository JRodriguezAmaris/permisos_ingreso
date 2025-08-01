"""Esquemas para las sucursales y estaciones."""
from typing import Optional
from pydantic import BaseModel
from app.models.branches import BranchTypes


class BranchSchema(BaseModel):
    """Esquema de sucursales y estaciones."""
    id: int
    name: str
    address: Optional[str]
    type: BranchTypes
    department_id: int
    municipality_id: int
    is_j10: bool

    class Config:
        from_attributes = True
