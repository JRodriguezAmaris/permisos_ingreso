"""Esquemas para los invitados."""
from pydantic import BaseModel
from typing import List, Optional

from app.schemas.places import MunicipalitySchema


class CompanyCreateSchema(BaseModel):
    """Esquema para crear compañias."""
    name: str
    nit: str | None = None
    is_eps: bool = False
    is_arl: bool = False

    class Config:
        from_attributes = True


class CompanySchema(CompanyCreateSchema):
    """Esquema para compañias."""
    id: int

    class Config:
        from_attributes = True


class GuestCreateSchema(BaseModel):
    """Esquema para crear invitados."""
    document_id: str
    name: str
    company_id: int
    eps_id: int
    arl_id: int
    city_id: int
    phone_number: str
    email: str

    class Config:
        from_attributes = True


class GuestUpdateSchema(BaseModel):
    document_id: Optional[str] = None
    name: Optional[str] = None
    eps_id: Optional[int] = None
    arl_id: Optional[int] = None
    company_id: Optional[int] = None
    city_id: Optional[int] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None

    class Config:
        from_attributes = True


class BulkGuestSchema(BaseModel):
    """Esquema para crear varios invitados."""
    guests: List[GuestCreateSchema]


class GuestIdSchema(BaseModel):
    """Esquema para ver los id de los invitados."""
    inserted_ids: List[int]
    updated_ids: List[int]
    guests_ids: List[int]


class GuestSchema(BaseModel):
    """Esquema de invitados."""
    id: int
    document_id: str
    name: str
    eps: CompanySchema | None = None
    arl: CompanySchema | None = None
    company: CompanySchema | None = None
    city: MunicipalitySchema | None = None
    phone_number: str
    email: str

    class Config:
        from_attributes = True


class UnitSchema(BaseModel):
    """Esquema de dependencia de un empleado"""
    id: int
    name: str

    class Config:
        from_attributes = True


class PositionSchema(BaseModel):
    """Esquema de cargo de un empleado"""
    id: int
    name: str

    class Config:
        from_attributes = True


class UserSchema(BaseModel):
    """Esquema de usuario"""
    id: int
    name: str
    unit: UnitSchema
    position: PositionSchema
    phone_number: str
    email: str

    class Config:
        from_attributes = True
