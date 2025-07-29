from fastapi import FastAPI
from app.routers import branches, users, places, entrances

app = FastAPI(title="My FastAPI Project")

app.include_router(branches.router, prefix="/api/branches", tags=["Sedes"])
app.include_router(places.router, prefix="/api/places", tags=["Ubicaciones"])
app.include_router(users.router, prefix="/api/users", tags=["Invitados"])
app.include_router(entrances.router, prefix="/api/entrances", tags=["Ingresos"])
