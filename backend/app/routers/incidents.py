"""CRUD endpoints for /api/incidents."""

import asyncio
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Employee, Incident, Shift
from app.schemas import IncidentCreateRequest, IncidentResponseEnriched
from app.services.calling_service import run_calling_simulation

router = APIRouter(prefix="/api/incidents", tags=["Incidents"])


def _next_incident_id(db: Session) -> str:
    """Generate next sequential INC-XXX id."""
    max_id = db.query(func.max(Incident.incident_id)).scalar()
    if max_id is None:
        return "INC-001"
    # Parse the numeric part from e.g. "INC-042"
    num = int(max_id.split("-")[1])
    return f"INC-{num + 1:03d}"


@router.get("/", response_model=list[IncidentResponseEnriched])
def list_incidents(
    status: Optional[str] = Query(None, description="Filter by incident status"),
    skip: int = Query(0, ge=0, description="Records to skip"),
    limit: int = Query(50, ge=1, le=200, description="Max records to return"),
    db: Session = Depends(get_db),
):
    """List incidents with enriched employee and shift details."""
    query = db.query(Incident)

    if status is not None:
        query = query.filter(Incident.status == status)

    incidents = query.offset(skip).limit(limit).all()
    result = []
    for inc in incidents:
        data = IncidentResponseEnriched.model_validate(inc).model_dump()

        # Enrich with employee name
        emp = db.query(Employee).filter(Employee.id == inc.original_employee_id).first()
        data["original_employee_name"] = emp.name if emp else ""

        # Enrich with shift details
        shift = db.query(Shift).filter(Shift.id == inc.shift_id).first()
        if shift:
            data["shift_date"] = shift.date
            data["shift_type"] = shift.shift_type
            data["role_required"] = shift.role_required
        else:
            data["shift_date"] = None
            data["shift_type"] = None
            data["role_required"] = None

        result.append(data)
    return result


@router.post("/", response_model=IncidentResponseEnriched, status_code=201)
async def create_incident(
    body: IncidentCreateRequest,
    db: Session = Depends(get_db),
):
    """Create a new incident with server-generated INC-XXX id.

    Spawns a background calling simulation that ranks candidates via ML,
    simulates calls with realistic delays, and broadcasts WebSocket events.
    """
    incident_id = _next_incident_id(db)

    db_incident = Incident(
        incident_id=incident_id,
        shift_id=body.shift_id,
        original_employee_id=body.original_employee_id,
        reason=body.reason,
        urgency=body.urgency,
        status="open",
    )
    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)

    # Build enriched response
    data = IncidentResponseEnriched.model_validate(db_incident).model_dump()

    emp = db.query(Employee).filter(Employee.id == db_incident.original_employee_id).first()
    data["original_employee_name"] = emp.name if emp else ""

    shift = db.query(Shift).filter(Shift.id == db_incident.shift_id).first()
    if shift:
        data["shift_date"] = shift.date
        data["shift_type"] = shift.shift_type
        data["role_required"] = shift.role_required

    # Spawn calling simulation as background task (non-blocking)
    asyncio.create_task(
        run_calling_simulation(db_incident.id, db_incident.shift_id)
    )

    return data
