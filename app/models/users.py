"""Modelos de usuarios."""
from sqlalchemy import CheckConstraint, Column, Integer, Boolean, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class Company(Base):
    """Modelo compañia."""
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)
    nit = Column(String, nullable=True)
    is_eps = Column(Boolean, default=False)
    is_arl = Column(Boolean, default=False)


class Guest(Base):
    """Modelo usuario invitado."""
    __tablename__ = "guests"

    id = Column(Integer, primary_key=True)
    document_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    eps_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    arl_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False)
    phone_number = Column(String, nullable=False, index=True)
    email = Column(String, nullable=False, index=True)

    eps  = relationship("Company", foreign_keys=[eps_id], backref="eps_guests")
    arl  = relationship("Company", foreign_keys=[arl_id], backref="arl_guests")
    company = relationship("Company", foreign_keys=[company_id], backref="company_guests")
    city = relationship("City", backref="guests")

    __table_args__ = (
        CheckConstraint("email LIKE '%@%.%'", name='check_email_format'),
        CheckConstraint(
            "phone_number GLOB '[0-9]*' AND LENGTH(phone_number) BETWEEN 10 AND 15",
            name='check_phone_number_format'
        ),
    )


class Unit(Base):
    """Modelo dependencia de un empleado"""
    __tablename__ = "units"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)


class Position(Base):
    """Modelo cargo de un empleado"""
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)


class User(Base):
    """Modelo usuario"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=False)
    position_id = Column(Integer, ForeignKey("positions.id"), nullable=False)
    phone_number = Column(String, nullable=False, index=True)
    email = Column(String, nullable=False, index=True)

    unit  = relationship("Unit", backref="users")
    position  = relationship("Position", backref="users")
    __table_args__ = (
        CheckConstraint("email LIKE '%@%.%'", name='check_email_format'),
        CheckConstraint(
            "phone_number GLOB '[0-9]*' AND LENGTH(phone_number) BETWEEN 10 AND 15",
            name='check_phone_number_format'
        ),
    )
