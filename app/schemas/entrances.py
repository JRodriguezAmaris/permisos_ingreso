"""Esquemas para las solicitudes de ingreso."""
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

from app.models.entrances import RequestStatus
from app.schemas.branches import BranchSchema
from app.schemas.users import GuestSchema, UserSchema


class MaterialCreateSchema(BaseModel):
    """Esquema para agregar los materiales de la solicitud de ingreso."""
    model: str
    serial: str | None = None
    description: str | None = None
    quantity: int = 1

    class Config:
        from_attributes = True


class MaterialSchema(MaterialCreateSchema):
    """Esquema para representar los materiales de la solicitud de ingreso."""
    id: int
    entrance_request_id: int

    class Config:
        from_attributes = True


class EntranceRequestCreateSchema(BaseModel):
    """Esquema para crear una solicitud de ingreso."""
    branch_id: int
    guests_ids: List[int]
    entry_date: datetime
    departure_date: datetime
    reason : str
    status : RequestStatus = RequestStatus.auth_pending
    is_installation : bool = False
    is_uninstallation : bool = False
    creator_id: int
    authorizer_id: int
    security_id: int | None = None
    materials: Optional[List[MaterialCreateSchema]] = []

    @field_validator("departure_date")
    def max_days_validation(cls, departure_date, values):
        """Valida que la fecha de salida no sea mayor a 30 días desde la fecha de ingreso."""
        entry_date = values.data.get("entry_date")
        if entry_date and (departure_date - entry_date).days > 30:
            raise ValueError("El permiso no puede ser mayor a 30 días")
        return departure_date


class EntranceRequestUpdateSchema(BaseModel):
    """Esquema para crear una solicitud de ingreso."""
    branch_id: Optional[int] = None
    entry_date: Optional[datetime] = None
    departure_date: Optional[datetime] = None
    reason: Optional[str] = None
    status: Optional[RequestStatus] = None
    is_installation : bool = False
    is_uninstallation : bool = False
    authorizer_id: Optional[int] = None
    security_id: Optional[int] = None
    guests_ids: Optional[List[int]] = None
    materials: Optional[List[MaterialCreateSchema]] = []

    class Config:
        from_attributes = True


class EntranceRequestSchema(BaseModel):
    """Esquema para representar una solicitud de ingreso."""
    id: int
    branch: BranchSchema
    guests: List[GuestSchema] = Field(..., alias="guests")
    materials: List[MaterialSchema] = Field(..., alias="materials")
    entry_date: datetime
    departure_date: datetime
    reason : str
    status : RequestStatus
    is_installation : bool
    is_uninstallation : bool
    creator: UserSchema | None = None
    authorizer: UserSchema | None = None
    security: UserSchema | None = None

    class Config:
        from_attributes = True

    @property
    def guest_list(self):
        return [g.guest for g in self.guests]
