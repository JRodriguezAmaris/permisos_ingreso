"""Script para exportar el formato excel de solicitudes de ingreso."""
import os
import shutil
from openpyxl import load_workbook
from sqlalchemy.orm import Session, selectinload

from app.models.branches import Branch, BranchTypes
from app.models.users import Guest, User
from app.models.entrances import EntranceRequest, EntranceRequestGuest


def export_entrance_requests_to_excel(
        db: Session, request_id: int, template_path: str, output_path: str):
    """Genera formato de ingreso a partir de una plantilla de Excel."""
    # Cargar datos de SQLAlchemy
    entrance_request = (
        db.query(EntranceRequest)
        .filter(EntranceRequest.id == request_id)
        .options(
            selectinload(EntranceRequest.branch),
            selectinload(EntranceRequest.branch).selectinload(Branch.municipality),
            selectinload(EntranceRequest.guests).selectinload(EntranceRequestGuest.guest),
            selectinload(EntranceRequest.guests)
                .selectinload(EntranceRequestGuest.guest)
                .selectinload(Guest.eps),
            selectinload(EntranceRequest.guests)
                .selectinload(EntranceRequestGuest.guest)
                .selectinload(Guest.arl),
            selectinload(EntranceRequest.guests)
                .selectinload(EntranceRequestGuest.guest)
                .selectinload(Guest.company),
            selectinload(EntranceRequest.authorizer),
            selectinload(EntranceRequest.authorizer)
                .selectinload(User.unit),
            selectinload(EntranceRequest.authorizer)
                .selectinload(User.position),
            selectinload(EntranceRequest.creator),
            selectinload(EntranceRequest.creator)
                .selectinload(User.unit),
            selectinload(EntranceRequest.creator)
                .selectinload(User.position),
            selectinload(EntranceRequest.security),
            selectinload(EntranceRequest.security)
                .selectinload(User.unit),
            selectinload(EntranceRequest.security)
                .selectinload(User.position),
        )
        .first()
    )

    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Plantilla no encontrada: {template_path}")

    # Copiar plantilla a archivo nuevo
    shutil.copy(template_path, output_path)

    # Cargar archivo copiado
    wb = load_workbook(output_path)
    ws = wb.active

    # Datos Generales
    ws.cell(row=6, column=2).value = entrance_request.branch.name.upper()
    ws.cell(row=6, column=5).value = entrance_request.branch.municipality.name.upper()
    if entrance_request.branch.type == BranchTypes.administrative:
        ws.cell(row=5, column=9).value = ""
        ws.cell(row=6, column=9).value = "x"
    else:
        ws.cell(row=5, column=9).value = "x"
        ws.cell(row=6, column=9).value = ""
    ws.cell(row=6, column=12).value = entrance_request.entry_date.strftime("%d/%m/%Y")
    ws.cell(row=6, column=15).value = entrance_request.departure_date.strftime("%d/%m/%Y")
    
    # Descripcion de las actividades
    ws.cell(row=9, column=2).value = entrance_request.reason.upper()
    
    # Relacion de ingreso y salida de personal a las instalaciones
    start_row = 15
    for idx, entrance_guest in enumerate(entrance_request.guests, start=start_row):
        ws.cell(row=idx, column=2).value = entrance_guest.guest.name
        ws.cell(row=idx, column=4).value = entrance_guest.guest.eps.name
        ws.cell(row=idx, column=5).value = entrance_guest.guest.arl.name
        ws.cell(row=idx, column=7).value = entrance_guest.guest.document_id
        ws.cell(row=idx, column=8).value = entrance_guest.guest.company.name
        ws.cell(row=idx, column=14).value = entrance_request.entry_date.strftime("%H:%M")
        ws.cell(row=idx, column=16).value = entrance_request.departure_date.strftime("%H:%M")

    #next_row = start_row + len(entrance_request.guests) + 13
    next_row = 76
    # Solicitante, autorizador y seguridad
    ws.cell(row=next_row, column=3).value = entrance_request.creator.name
    ws.cell(row=next_row, column=8).value = entrance_request.authorizer.name
    ws.cell(row=next_row, column=15).value = entrance_request.security.name

    ws.cell(row=next_row + 1, column=3).value = entrance_request.creator.unit.name
    ws.cell(row=next_row + 1, column=8).value = entrance_request.authorizer.unit.name
    ws.cell(row=next_row + 1, column=15).value = entrance_request.security.unit.name

    ws.cell(row=next_row + 2, column=3).value = entrance_request.creator.position.name
    ws.cell(row=next_row + 2, column=8).value = entrance_request.authorizer.position.name
    ws.cell(row=next_row + 2, column=15).value = entrance_request.security.position.name

    ws.cell(row=next_row + 3, column=3).value = entrance_request.creator.phone_number
    ws.cell(row=next_row + 3, column=8).value = entrance_request.authorizer.phone_number
    ws.cell(row=next_row + 3, column=15).value = entrance_request.security.phone_number

    wb.save(output_path)
    print(f"Archivo generado: {output_path}")
