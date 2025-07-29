"""Modelos de sedes y estaciones."""
from enum import Enum as Enum_py
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Enum
from sqlalchemy.orm import relationship
from app.db.database import Base


class BranchTypes(str, Enum_py):
    """Representa los tipos de sedes."""
    administrative = "Administrativa"
    technical = "Técnica"
    external = "Externa"


class Branch(Base):
    """Modelo sedes."""
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    address = Column(String)
    type = Column(Enum(BranchTypes), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    municipality_id = Column(Integer, ForeignKey("municipalities.id"), nullable=False)
    is_j10 = Column(Boolean, default=False)
    
    department = relationship("Department", backref="branches")
    municipality = relationship("Municipality", backref="branches")
