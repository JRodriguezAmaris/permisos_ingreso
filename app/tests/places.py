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
        Department(id=2, name="Antioquia", cod_dane="05"),
        Department(id=3, name="Atlantico", cod_dane="08"),
    ]
    db.add_all(department)
    db.query(Municipality).delete()
    municipality = [
        Municipality(id=1, name="Bogota", cod_dane="11001", department_id=1),
        Municipality(id=2, name="Medellin", cod_dane="05001", department_id=2),
        Municipality(id=3, name="Bello", cod_dane="05014", department_id=2),
        Municipality(id=4, name="Barranquilla", cod_dane="08001", department_id=3),
        Municipality(id=5, name="Soledad", cod_dane="08015", department_id=3),
    ]
    db.add_all(municipality)
    db.commit()
    yield
    db.close()


def test_get_all_departments():
    """Prueba para obtener todos los departamentos."""
    response = client.get("/api/places/departments")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 3
    assert data["total"] == len(data["items"])


def test_get_all_municipalities():
    """Prueba para obtener todos los municipios."""
    response = client.get("/api/places/municipalities")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 5
    assert data["total"] == len(data["items"])


def test_search_by_department_name():
    """Prueba para obtener los departamentos filtrados por nombre."""
    response = client.get("/api/places/departments?name=Ant")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert data["items"][0]["name"] == "Antioquia"


def test_search_by_municipality_name():
    """Prueba para obtener los municipios filtrados por nombre."""
    response = client.get("/api/places/municipalities?name=Bello")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert "05" in data["items"][0]["cod_dane"]


def test_search_by_municipality_department():
    """Prueba para obtener los municipios filtrados por departamento."""
    response = client.get("/api/places/municipalities?department_id=3")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert "08" in data["items"][0]["cod_dane"]
