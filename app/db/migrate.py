"""Script para migrar los modelos a la base de datos."""
from app.db.database import Base, engine
from app.models.branches import Branch  # noqa: F401
from app.models.places import City, Department, Municipality  # noqa: F401
from app.models.users import Guest  # noqa: F401
from app.models.entrances import EntranceRequest  # noqa: F401

Base.metadata.create_all(bind=engine)
