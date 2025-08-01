"""Tests unitarios para el endpoint de sucursales."""
import pytest
from fastapi.testclient import TestClient
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base, get_db
from app.auth.dependencies import get_current_user
from app.models.branches import Branch, BranchTypes
from app.models.places import Department, Municipality
from app.main import app

# Crear una BD para pruebas
SQLALCHEMY_DATABASE_URL = "sqlite:///./unit_test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Sobrescribe la función get_db para usar la BD de pruebas."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    """Emula la función get_current_user para pruebas."""
    return {
        "sub": "testuser",
        "id": 1,
        "role": "admin",
    }


app.dependency_overrides[get_current_user] = override_get_current_user
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# Crear tablas
Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function", autouse=True)
def setup_data():
    """Configura los datos necesarios para las pruebas."""
    db = TestingSessionLocal()
    # Places
    db.query(Department).delete()
    department = [
        Department(id=1, name="Bogota DC", cod_dane="11"),
    ]
    db.add_all(department)
    db.query(Municipality).delete()
    municipality = [
        Municipality(id=1, name="Bogota", cod_dane="11001", department_id=1),
    ]
    db.add_all(municipality)
    # Branches
    db.query(Branch).delete()
    branches = [
        Branch(code="s1234", name="Sede Administrativa", address="Calle 123", type=BranchTypes.administrative, department_id=1, municipality_id=1),
        Branch(code="s1235", name="Sede Tecnica", address="Carrera 46", type=BranchTypes.technical, department_id=1, municipality_id=1),
        Branch(code="s1236", name="Sede Tecnica Externa", address="Diagonal 9", type=BranchTypes.external, department_id=1, municipality_id=1),
    ]
    db.add_all(branches)
    db.commit()
    yield
    db.close()


def test_get_all_branches():
    """Prueba para obtener todas las sucursales."""
    response = client.get("/api/branches/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3


def test_pagination_limit_offset():
    """Prueba de paginación con límite y desplazamiento."""
    response = client.get("/api/branches/?limit=2&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["total"] == 3


def test_filter_by_branch_type():
    """Prueba de filtrado por tipo de sucursal."""
    response = client.get("/api/branches/?branch_type=Administrativa")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert all(branch["type"] == "Administrativa" for branch in data["items"])


def test_search_by_name():
    """Prueba de búsqueda por nombre de sucursal."""
    response = client.get("/api/branches/?search=externa")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Sede Tecnica Externa"
