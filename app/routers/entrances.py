"""Rutas para la creacion de solicitudes de ingreso."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Body, Query
from sqlalchemy.orm import Session, selectinload

from app.db.database import get_db
from app.models.entrances import Material, EntranceRequest, EntranceRequestGuest, RequestStatus
from app.models.branches import Branch
from app.models.users import Guest, User
from app.schemas.entrances import (
    EntranceRequestCreateSchema,
    EntranceRequestUpdateSchema,
    EntranceRequestSchema
)
from app.utils.email import send_email_with_attachments
from app.utils.pagination import PaginatedResponse, paginate
from app.scripts.create_format import export_entrance_requests_to_excel

router = APIRouter()


@router.post("/requests", response_model=EntranceRequestSchema, status_code=201)
def create_entrance_request(
    data: EntranceRequestCreateSchema,
    db: Session = Depends(get_db),
):
    """Crea una solicitud de entrada."""
    # Valida que la sede exista
    branch = db.query(Branch).filter(Branch.id == data.branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Sede no encontrada")
    # Crea la solicitud de ingreso
    entrance_data = data.model_dump(exclude={"guests_ids", "materials"})
    entrance_request = EntranceRequest(**entrance_data)
    db.add(entrance_request)
    db.flush()
    # Procesa los invitados
    for guest_id in data.guests_ids:
        # # Crear o recuperar el invitado
        guest = db.query(Guest).filter(Guest.id == guest_id).first()
        if not guest:
            continue
        # Relación con la solicitud
        link = EntranceRequestGuest(
            entrance_request_id=entrance_request.id,
            guest_id=guest_id,
        )
        db.add(link)
    # Procesa los equipos o materiales
    for material_data in data.materials:
        material = Material(
            entrance_request_id=entrance_request.id,
            **material_data.model_dump()
        )
        db.add(material)
    db.commit()

    entrance_request = (
        db.query(EntranceRequest)
        .options(
            selectinload(EntranceRequest.branch),
            selectinload(EntranceRequest.guests).selectinload(EntranceRequestGuest.guest),
            selectinload(EntranceRequest.creator),
            selectinload(EntranceRequest.authorizer),
            selectinload(EntranceRequest.security),
            selectinload(EntranceRequest.materials),
        )
        .filter(EntranceRequest.id == entrance_request.id)
        .first()
    )
    return EntranceRequestSchema(
        id=entrance_request.id,
        branch=entrance_request.branch,
        guests=[guest.guest for guest in entrance_request.guests],
        entry_date=entrance_request.entry_date,
        departure_date=entrance_request.departure_date,
        reason=entrance_request.reason,
        status=entrance_request.status,
        is_installation=entrance_request.is_installation,
        is_uninstallation=entrance_request.is_uninstallation,
        creator=entrance_request.creator,
        authorizer=entrance_request.authorizer,
        security=entrance_request.security,
        materials=[material for material in entrance_request.materials]
    )


@router.get("/requests/{request_id}", response_model=EntranceRequestSchema)
def get_entrance_request(
    request_id: int,
    db: Session = Depends(get_db),
):
    """Obtiene una solicitud de ingreso por ID."""
    entrance_request = (
        db.query(EntranceRequest)
        .options(
            selectinload(EntranceRequest.branch),
            selectinload(EntranceRequest.guests).selectinload(EntranceRequestGuest.guest),
            selectinload(EntranceRequest.creator),
            selectinload(EntranceRequest.authorizer),
            selectinload(EntranceRequest.security),
        )
        .filter(EntranceRequest.id == request_id)
        .first()
    )
    if not entrance_request:
        raise HTTPException(status_code=404, detail="Solicitud de ingreso no encontrada")

    return EntranceRequestSchema(
        id=entrance_request.id,
        branch=entrance_request.branch,
        guests=[guest.guest for guest in entrance_request.guests],
        entry_date=entrance_request.entry_date,
        departure_date=entrance_request.departure_date,
        reason=entrance_request.reason,
        status=entrance_request.status,
        is_installation=entrance_request.is_installation,
        is_uninstallation=entrance_request.is_uninstallation,
        creator=entrance_request.creator,
        authorizer=entrance_request.authorizer,
        security=entrance_request.security,
        materials=[material for material in entrance_request.materials]
    )


@router.get("/requests", response_model=PaginatedResponse[EntranceRequestSchema])
def get_entrance_requests(
    status: Optional[RequestStatus] = Query(None, description="Filtrar por estado de solicitud"),
    security_id: Optional[int] = Query(None, description="Filtrar por ID de seguridad"),
    creator_id: Optional[int] = Query(None, description="Filtrar por ID de creador"),
    authorizer_id: Optional[int] = Query(None, description="Filtrar por ID de autorizador"),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, le=100),
    db: Session = Depends(get_db),
):
    """Obtiene una lista de solicitudes, opcionalmente filtradas por estado."""
    query = db.query(EntranceRequest)
    if status:
        query = query.filter(EntranceRequest.status == status)
    if security_id:
        query = query.filter(EntranceRequest.security_id == security_id)
    if creator_id:
        query = query.filter(EntranceRequest.creator_id == creator_id)
    if authorizer_id:
        query = query.filter(EntranceRequest.authorizer_id == authorizer_id)
    query = (
        query.options(
            selectinload(EntranceRequest.branch),
            selectinload(EntranceRequest.guests).selectinload(EntranceRequestGuest.guest),
            selectinload(EntranceRequest.creator),
            selectinload(EntranceRequest.authorizer),
            selectinload(EntranceRequest.security),
            selectinload(EntranceRequest.materials),
        ).order_by(EntranceRequest.entry_date.desc())
    )
    return paginate(query, EntranceRequestSchema, offset=offset, limit=limit)


@router.put("/requests/{request_id}", response_model=EntranceRequestSchema)
def update_entrance_request(
    request_id: int,
    data: EntranceRequestUpdateSchema = Body(...),
    db: Session = Depends(get_db),
):
    """Actualiza una solicitud de ingreso."""
    # Buscar la solicitud existente
    entrance_request = db.query(EntranceRequest).filter(EntranceRequest.id == request_id).first()
    if not entrance_request:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    # Actualizar campos si vienen en el body
    update_data = data.model_dump(exclude_unset=True)

    # Validar branch si se actualiza
    if "branch_id" in update_data:
        branch = db.query(Branch).filter(Branch.id == update_data["branch_id"]).first()
        if not branch:
            raise HTTPException(status_code=404, detail="Sede no encontrada")

    # Validar authorizer si se actualiza
    if "authorizer_id" in update_data:
        auth = db.query(User).filter(User.id == update_data["authorizer_id"]).first()
        if not auth:
            raise HTTPException(status_code=404, detail="Autorizador no encontrado")

    # Validar security si se actualiza
    if "security_id" in update_data:
        sec = db.query(User).filter(User.id == update_data["security_id"]).first()
        if not sec:
            raise HTTPException(status_code=404, detail="Personal de seguridad no encontrado")

    # Actualizar campos en el modelo
    for field, value in update_data.items():
        if field != "guests_ids":
            setattr(entrance_request, field, value)

    # Actualizar invitados si vienen
    if "guests_ids" in update_data:
        db.query(EntranceRequestGuest).filter(
            EntranceRequestGuest.entrance_request_id == request_id
        ).delete()
        for guest_id in update_data["guests_ids"]:
            guest = db.query(Guest).filter(Guest.id == guest_id).first()
            if not guest:
                raise HTTPException(
                    status_code=404,
                    detail=f"Invitado con ID {guest_id} no encontrado"
                )
            db.add(EntranceRequestGuest(entrance_request_id=request_id, guest_id=guest_id))

    db.commit()

    if update_data.get('status') == RequestStatus.authorized:
        export_entrance_requests_to_excel(
            db, request_id, "format_templates/PERMISO MOVISTAR.xlsx", f"output_{request_id}.xlsx"
        )
        send_email_with_attachments(
            file_name=f"output_{request_id}.xlsx",
            recipients=[entrance_request.creator.email, entrance_request.authorizer.email]
        )

    entrance_request = (
        db.query(EntranceRequest)
        .options(
            selectinload(EntranceRequest.branch),
            selectinload(EntranceRequest.guests).selectinload(EntranceRequestGuest.guest),
            selectinload(EntranceRequest.creator),
            selectinload(EntranceRequest.authorizer),
            selectinload(EntranceRequest.security),
            selectinload(EntranceRequest.materials),
        )
        .filter(EntranceRequest.id == request_id)
        .first()
    )

    return EntranceRequestSchema(
        id=entrance_request.id,
        branch=entrance_request.branch,
        guests=[guest.guest for guest in entrance_request.guests],
        entry_date=entrance_request.entry_date,
        departure_date=entrance_request.departure_date,
        reason=entrance_request.reason,
        creator=entrance_request.creator,
        status=entrance_request.status,
        is_installation=entrance_request.is_installation,
        is_uninstallation=entrance_request.is_uninstallation,
        authorizer=entrance_request.authorizer,
        security=entrance_request.security,
        materials=[material for material in entrance_request.materials]
    )
