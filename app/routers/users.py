"""Rutas para manejar los usuarios de la aplicación."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.models.users import Company, Guest, User
from app.schemas.users import (
    BulkGuestSchema,
    CompanyCreateSchema,
    CompanySchema,
    GuestIdSchema,
    GuestSchema,
    GuestUpdateSchema,
    UserSchema
)
from app.utils.pagination import paginate, PaginatedResponse

router = APIRouter()


@router.get("/companies", response_model=PaginatedResponse[CompanySchema])
def get_companies(
    name: Optional[str] = Query(None, description="Buscar por nombre de empresa"),
    is_eps: Optional[bool] = Query(None, description="Buscar las eps"),
    is_arl: Optional[bool] = Query(None, description="Buscar las arl"),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, le=100),
    db: Session = Depends(get_db),
):
    """
    Obtiene una lista de empresas, opcionalmente filtradas por nombre, si son eps y si son arl.
    """
    query = db.query(Company)
    if name:
        query = query.filter(Company.name.ilike(f"%{name.lower()}%"))
    if is_eps:
        query = query.filter(Company.is_eps == is_eps)
    if is_arl:
        query = query.filter(Company.is_arl == is_arl)
    return paginate(query, CompanySchema, offset=offset, limit=limit)


@router.post("/companies", response_model=CompanySchema)
def create_companies(
    data: CompanyCreateSchema,
    db: Session = Depends(get_db),
):
    """Crea los datos de compañias."""
    data.name = data.name.capitalize().strip()
    company = db.query(Company).filter(Company.name.ilike(f"%{data.name}%")).first()
    if company:
        return company
    company = Company(**data.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@router.get("/", response_model=PaginatedResponse[UserSchema])
def get_users(
    email: Optional[str] = Query(None, description="Buscar por email"),
    name: Optional[str] = Query(None, description="Buscar por nombre"),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, le=100),
    db: Session = Depends(get_db),
):
    """Obtiene una lista de invitados, opcionalmente filtrados por documento, empresa o ciudad."""
    query = db.query(User)
    if email:
        query = query.filter(User.email.ilike(f"%{email}%"))
    if name:
        query = query.filter(User.name.ilike(f"%{name}%"))
    return paginate(query, UserSchema, offset=offset, limit=limit)


@router.get("/guests", response_model=PaginatedResponse[GuestSchema])
def get_guests(
    document_id: Optional[str] = Query(None, description="Buscar por documento"),
    company_id: Optional[int] = Query(None, description="Buscar por empresa"),
    city_id: Optional[int] = Query(None, description="Buscar por documento"),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, le=100),
    db: Session = Depends(get_db),
):
    """Obtiene una lista de invitados, opcionalmente filtrados por documento, empresa o ciudad."""
    query = db.query(Guest)
    if document_id:
        query = query.filter(Guest.document_id == document_id)
    if company_id:
        query = query.filter(Guest.company_id == company_id)
    if city_id:
        query = query.filter(Guest.city_id == city_id)
    return paginate(query, GuestSchema, offset=offset, limit=limit)


@router.post("/guests", response_model=GuestIdSchema)
def create_guests(payload: BulkGuestSchema, db: Session = Depends(get_db)):
    """Crea varios invitados al tiempo."""
    incoming_document_ids = [guest.document_id for guest in payload.guests]

    # Buscar los que ya existen en la DB
    existing_guests = db.query(Guest).filter(
        Guest.document_id.in_(incoming_document_ids)
    ).all()
    existing_dict = {guest.document_id: guest for guest in existing_guests}

    inserted_ids = []
    updated_ids = []

    for guest_data in payload.guests:
        doc_id = guest_data.document_id
        if doc_id in existing_dict:
            # Actualizar invitados existentes
            existing = existing_dict[doc_id]
            existing.name = guest_data.name
            existing.eps_id = guest_data.eps_id
            existing.arl_id = guest_data.arl_id
            existing.company_id = guest_data.company_id
            existing.city_id = guest_data.city_id
            existing.phone_number = guest_data.phone_number
            existing.email = guest_data.email
            updated_ids.append(existing.id)
        else:
            # Crear nuevos invitados
            new_guest = Guest(
                document_id=guest_data.document_id,
                name=guest_data.name,
                eps_id=guest_data.eps_id,
                arl_id=guest_data.arl_id,
                company_id=guest_data.company_id,
                city_id=guest_data.city_id,
                phone_number=guest_data.phone_number,
                email=guest_data.email
            )
            db.add(new_guest)
            db.flush()
            inserted_ids.append(new_guest.id)
    db.commit()
    return {
        "inserted_ids": inserted_ids,
        "updated_ids": updated_ids,
        "guests_ids": inserted_ids + updated_ids
    }


@router.put("/guests/{guest_id}", response_model=GuestSchema)
def update_guest(guest_id: int, data: GuestUpdateSchema, db: Session = Depends(get_db)):
    guest = db.query(Guest).filter(Guest.id == guest_id).first()
    if not guest:
        raise HTTPException(status_code=404, detail="Guest not found")

    for field, value in data.dict(exclude_unset=True).items():
        setattr(guest, field, value)

    db.commit()
    db.refresh(guest)
    return guest
