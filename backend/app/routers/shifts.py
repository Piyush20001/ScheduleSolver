"""CRUD endpoints for /api/shifts."""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Employee, Shift
from app.schemas import ShiftCreate, ShiftResponse, ShiftResponseEnriched

router = APIRouter(prefix="/api/shifts", tags=["Shifts"])


@router.get("/", response_model=list[ShiftResponseEnriched])
def list_shifts(
    start_date: Optional[date] = Query(None, description="Filter shifts on or after this date"),
    end_date: Optional[date] = Query(None, description="Filter shifts on or before this date"),
    db: Session = Depends(get_db),
):
    """List shifts with optional date range filter and enriched employee name."""
    query = db.query(Shift)

    if start_date is not None:
        query = query.filter(Shift.date >= start_date)
    if end_date is not None:
        query = query.filter(Shift.date <= end_date)

    shifts = query.all()
    result = []
    for shift in shifts:
        data = ShiftResponseEnriched.model_validate(shift).model_dump()
        if shift.assigned_employee_id is not None:
            emp = db.query(Employee).filter(Employee.id == shift.assigned_employee_id).first()
            data["assigned_employee_name"] = emp.name if emp else None
        else:
            data["assigned_employee_name"] = None
        result.append(data)
    return result


@router.post("/", response_model=ShiftResponse, status_code=201)
def create_shift(
    shift: ShiftCreate,
    db: Session = Depends(get_db),
):
    """Create a new shift."""
    db_shift = Shift(**shift.model_dump())
    db.add(db_shift)
    db.commit()
    db.refresh(db_shift)
    return db_shift
