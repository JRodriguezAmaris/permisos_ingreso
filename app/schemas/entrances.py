"""Esquemas para las solicitudes de ingreso."""
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

from app.models.entrances import RequestStatus
from app.schemas.branches import BranchSchema
from app.schemas.users import GuestCreateSchema, GuestSchema, UserSchema


class EntranceRequestCreateSchema(BaseModel):
    """Esquema para crear una solicitud de ingreso."""
    branch_id: int
    guests: List[GuestCreateSchema]
    entry_date: datetime
    departure_date: datetime
    reason : str
    status : RequestStatus = RequestStatus.auth_pending
    creator_id: int
    authorizer_id: int
    security_id: int | None = None

    @field_validator("departure_date")
    def max_days_validation(cls, departure_date, values):
        """Valida que la fecha de salida no sea mayor a 30 días desde la fecha de ingreso."""
        entry_date = values.data.get("entry_date")
        if entry_date and (departure_date - entry_date).days > 30:
            raise ValueError("El permiso no puede ser mayor a 30 días")
        return departure_date


class EntranceRequestUpdateSchema(BaseModel):
    """Esquema para crear una solicitud de ingreso."""
    branch_id: Optional[int]
    entry_date: Optional[datetime]
    departure_date: Optional[datetime]
    reason: Optional[str]
    status: Optional[RequestStatus]
    authorizer_id: Optional[int]
    security_id: Optional[int]
    guests: Optional[List[int]]

    class Config:
        orm_mode = True


class EntranceRequestSchema(BaseModel):
    """Esquema para representar una solicitud de ingreso."""
    id: int
    branch: BranchSchema
    guests: List[GuestSchema] = Field(..., alias="guest_list")
    entry_date: datetime
    departure_date: datetime
    reason : str
    status : RequestStatus
    creator: UserSchema | None = None
    authorizer: UserSchema | None = None
    security: UserSchema | None = None

    class Config:
        from_attributes = True
        orm_mode = True

    @property
    def guest_list(self):
        return [g.guest for g in self.guests]
