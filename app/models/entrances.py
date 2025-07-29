"""Modelos de solicitud de ingreso."""
from enum import Enum as Enum_py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, CheckConstraint
from sqlalchemy.orm import relationship
from app.db.database import Base


class RequestStatus(str, Enum_py):
    """Representa los tipos de estados de una solicitud."""
    approved = "Autorizado"
    refused = "Rechazado"
    auth_pending = "Pendiente por autorizador"
    security_pending = "Pendiente por seguridad"


class EntranceRequest(Base):
    """Modelo solicitudes de ingreso."""
    __tablename__ = "entrance_requests"

    id = Column(Integer, primary_key=True, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    entry_date = Column(DateTime, nullable=False)
    departure_date = Column(DateTime, nullable=False)
    reason = Column(String, nullable=False)
    status = Column(Enum(RequestStatus), default=False)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    authorizer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    security_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    branch = relationship("Branch", backref="entrance_requests")
    creator = relationship("User", foreign_keys=[creator_id], backref="creator_requests")
    authorizer = relationship("User", foreign_keys=[authorizer_id], backref="auth_requests")
    security = relationship("User", foreign_keys=[security_id], backref="security_requests")

    __table_args__ = (
        CheckConstraint("departure_date >= entry_date", name="validate_dates"),
    )

    @property
    def guest_list(self):
        return [g.guest for g in self.guests]


class EntranceRequestGuest(Base):
    """Modelo invitados con solicitudes de ingreso."""
    __tablename__ = "entrance_requests_guests"

    id = Column(Integer, primary_key=True, index=True)
    entrance_request_id = Column(Integer, ForeignKey("entrance_requests.id"), nullable=False)
    guest_id = Column(Integer, ForeignKey("guests.id"), nullable=False)

    entrance_request = relationship("EntranceRequest", backref="guests")
    guest = relationship("Guest", backref="entrance_requests")
