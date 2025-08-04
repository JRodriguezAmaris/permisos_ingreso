from fastapi import FastAPI, Depends
from fastapi.openapi.utils import get_openapi
from app.routers import branches, users, places, entrances
from app.auth.dependencies import get_current_user

app = FastAPI()

app.include_router(
    branches.router,
    prefix="/api/branches",
    tags=["Sedes"],
    dependencies=[Depends(get_current_user)]
)
app.include_router(
    places.router,
    prefix="/api/places",
    tags=["Ubicaciones"],
    dependencies=[Depends(get_current_user)]
)
app.include_router(
    users.router,
    prefix="/api/users",
    tags=["Invitados"],
    dependencies=[Depends(get_current_user)]
)
app.include_router(
    entrances.router,
    prefix="/api/entrances",
    tags=["Ingresos"],
    dependencies=[Depends(get_current_user)]
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Permisos de Ingreso API",
        version="1.0.0",
        description=(
            "APIs diseñadas para gestionar los permisos de ingreso a las sedes de Telefónica."
        ),
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
