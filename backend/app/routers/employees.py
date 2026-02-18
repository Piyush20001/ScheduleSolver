"""CRUD endpoints for /api/employees."""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Employee
from app.schemas import EmployeeCreate, EmployeeResponse

router = APIRouter(prefix="/api/employees", tags=["Employees"])


@router.get("/", response_model=list[EmployeeResponse])
def list_employees(
    role: Optional[str] = Query(None, description="Filter by role"),
    weekend_available: Optional[bool] = Query(None, description="Filter by weekend availability"),
    min_reliability: Optional[float] = Query(None, description="Minimum reliability score"),
    db: Session = Depends(get_db),
):
    """List active employees with optional filters."""
    query = db.query(Employee).filter(Employee.is_active == True)  # noqa: E712

    if role is not None:
        query = query.filter(Employee.role == role)
    if weekend_available is not None:
        query = query.filter(Employee.weekend_available == weekend_available)
    if min_reliability is not None:
        query = query.filter(Employee.reliability_score >= min_reliability)

    return query.all()


@router.post("/", response_model=EmployeeResponse, status_code=201)
def create_employee(
    employee: EmployeeCreate,
    db: Session = Depends(get_db),
):
    """Create a new employee."""
    db_employee = Employee(**employee.model_dump())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee
