"""Modulo para manejar la conexión a la base de datos y crear el motor SQLAlchemy."""
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from app.config.settings import settings

DATABASE_URL = settings.DB_URL

print(f"Conectando a la base de datos en: {DATABASE_URL}")

# Crea el motor de la base de datos
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Crear SessionLocal para cada request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative Base (heredado por los modelos)
Base = declarative_base()


def get_db() -> Session | Generator[Session]:
    """Obtiene una sesión de base de datos para usar en las rutas."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
