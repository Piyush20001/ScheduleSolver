"""Recommendations router: ML-powered candidate ranking for shifts."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.ml.data_generator import COMPATIBLE_ROLES
from app.models import Employee, Shift
from app.schemas import RankRequest, RankResponse
from app.services import ml_service

router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])


@router.post("/rank", response_model=RankResponse)
def rank_candidates(request: RankRequest, db: Session = Depends(get_db)):
    """Rank compatible employees for a shift using ML inference.

    Returns candidates sorted by predicted acceptance probability,
    each with a human-readable reason string highlighting top 3 factors.
    """
    # Look up shift
    shift = db.query(Shift).filter(Shift.id == request.shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")

    # Find compatible roles for this shift's required role
    compatible_roles = COMPATIBLE_ROLES.get(shift.role_required, {shift.role_required})

    # Query active employees with compatible roles
    compatible_employees = (
        db.query(Employee)
        .filter(Employee.is_active == True, Employee.role.in_(compatible_roles))  # noqa: E712
        .all()
    )

    # Rank using ML
    candidates = ml_service.rank_candidates(shift, compatible_employees)

    return RankResponse(
        shift_id=shift.id,
        role_required=shift.role_required,
        candidates=candidates,
    )
