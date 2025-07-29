"""Modelos de lugares."""
from sqlalchemy import Column, ForeignKey, CheckConstraint, Integer, String
from sqlalchemy.orm import relationship
from app.db.database import Base


class Department(Base):
    """Modelo departamentos."""
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    cod_dane = Column(String, nullable=False, unique=True)

    __table_args__ = (
        CheckConstraint("cod_dane IS NOT NULL", name="cod_dane_not_null"),
    )


class Municipality(Base):
    """Modelo municipios."""
    __tablename__ = "municipalities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    cod_dane = Column(String, nullable=False, unique=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)

    department = relationship("Department", backref="municipalities")
    __table_args__ = (
        CheckConstraint("cod_dane IS NOT NULL", name="cod_dane_not_null"),
    )


class City(Base):
    """Modelo municipios."""
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    municipality_id = Column(Integer, ForeignKey("municipalities.id"), nullable=False)

    municipality = relationship("Municipality", backref="cities")
