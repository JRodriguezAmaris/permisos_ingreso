"""Script para migrar los modelos a la base de datos."""
from app.db.database import Base, engine
from app.models.branches import Branch
from app.models.places import City, Department, Municipality
from app.models.users import Guest
from app.models.entrances import EntranceRequest

Base.metadata.create_all(bind=engine)
