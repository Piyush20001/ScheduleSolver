"""Simulated autonomous calling service with WebSocket broadcasting."""

import asyncio
import logging
import random
from datetime import datetime, timezone

from app.database import SessionLocal
from app.ml.data_generator import COMPATIBLE_ROLES
from app.models import CallLog, Employee, Incident, Shift
from app.services import ml_service
from app.websocket import manager

logger = logging.getLogger(__name__)

# Probability weights per ML score tier: [accepted, declined, no_answer, voicemail]
OUTCOME_WEIGHTS = {
    "high": [0.70, 0.15, 0.10, 0.05],  # score > 0.8
    "medium": [0.40, 0.25, 0.20, 0.15],  # 0.5 <= score <= 0.8
    "low": [0.15, 0.30, 0.30, 0.25],  # score < 0.5
}
OUTCOMES = ["accepted", "declined", "no_answer", "voicemail"]
MAX_CANDIDATES = 5


def _get_score_tier(score: float) -> str:
    if score > 0.8:
        return "high"
    if score >= 0.5:
        return "medium"
    return "low"


def _pick_outcome(score: float) -> str:
    tier = _get_score_tier(score)
    weights = OUTCOME_WEIGHTS[tier]
    return random.choices(OUTCOMES, weights=weights, k=1)[0]


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


async def run_calling_simulation(
    incident_db_id: int,
    shift_id: int,
    delay_multiplier: float = 1.0,
):
    """Run the calling simulation as a background async task.

    Args:
        incident_db_id: Primary key of the Incident row.
        shift_id: Primary key of the Shift row to fill.
        delay_multiplier: Scale factor for sleep delays (0.01 for tests, 1.0 for production).
    """
    # --- Load data with fresh session (RT-06: own DB session) ---
    session = SessionLocal()
    try:
        incident = session.query(Incident).filter(Incident.id == incident_db_id).first()
        shift = session.query(Shift).filter(Shift.id == shift_id).first()
        if not incident or not shift:
            logger.error(f"Incident {incident_db_id} or Shift {shift_id} not found")
            return

        # Get compatible employees for this shift's role
        compatible_roles = COMPATIBLE_ROLES.get(shift.role_required, {shift.role_required})
        employees = (
            session.query(Employee)
            .filter(
                Employee.is_active == True,  # noqa: E712
                Employee.role.in_(compatible_roles),
                Employee.id != incident.original_employee_id,  # Exclude the absent employee
            )
            .all()
        )

        if not employees:
            # No eligible candidates -- escalate immediately
            incident.status = "escalated"
            session.commit()
            await manager.broadcast({
                "type": "incident_escalated",
                "timestamp": _now_utc().isoformat(),
                "incident_id": incident.incident_id,
                "data": {
                    "reason": "No eligible candidates found",
                    "total_calls": 0,
                },
            })
            return

        # Rank candidates via ML
        ranked = ml_service.rank_candidates(shift, employees)
        top_candidates = ranked[:MAX_CANDIDATES]
    finally:
        session.close()

    # --- Broadcast incident_created ---
    session = SessionLocal()
    try:
        incident = session.query(Incident).filter(Incident.id == incident_db_id).first()
        shift = session.query(Shift).filter(Shift.id == shift_id).first()
        original_emp = session.query(Employee).filter(
            Employee.id == incident.original_employee_id
        ).first()

        await manager.broadcast({
            "type": "incident_created",
            "timestamp": _now_utc().isoformat(),
            "incident_id": incident.incident_id,
            "data": {
                "incident_db_id": incident.id,
                "shift_id": shift.id,
                "shift_date": shift.date.isoformat(),
                "shift_type": shift.shift_type,
                "role_required": shift.role_required,
                "original_employee": original_emp.name if original_emp else "",
                "reason": incident.reason,
                "urgency": incident.urgency,
                "candidates_count": len(top_candidates),
            },
        })

        # Transition to in_progress (when first call starts)
        incident.status = "in_progress"
        session.commit()
    finally:
        session.close()

    # --- Call candidates sequentially ---
    resolved = False
    for call_order, candidate in enumerate(top_candidates, start=1):
        call_started_at = _now_utc()
        employee_id = candidate["employee_id"]
        ml_score = candidate["score"]

        # Broadcast calling_candidate (ringing phase)
        await manager.broadcast({
            "type": "calling_candidate",
            "timestamp": call_started_at.isoformat(),
            "incident_id": incident.incident_id,
            "data": {
                "call_order": call_order,
                "total_candidates": len(top_candidates),
                "employee_id": employee_id,
                "name": candidate["name"],
                "role": candidate["role"],
                "ml_score": ml_score,
                "reason": candidate["reason"],
            },
        })

        # Ringing delay: 1-2 seconds
        await asyncio.sleep(random.uniform(1.0, 2.0) * delay_multiplier)

        # Determine outcome
        outcome = _pick_outcome(ml_score)
        call_ended_at = _now_utc()
        duration = int((call_ended_at - call_started_at).total_seconds())

        # Log call to database (RT-05)
        session = SessionLocal()
        try:
            call_log = CallLog(
                incident_id=incident_db_id,
                employee_id=employee_id,
                call_order=call_order,
                status=outcome,
                ml_score=ml_score,
                call_started_at=call_started_at,
                call_ended_at=call_ended_at,
                duration_seconds=duration,
                notes=f"Tier: {_get_score_tier(ml_score)}, Auto-simulated",
            )
            session.add(call_log)
            session.commit()
        finally:
            session.close()

        # Broadcast call_result
        await manager.broadcast({
            "type": "call_result",
            "timestamp": call_ended_at.isoformat(),
            "incident_id": incident.incident_id,
            "data": {
                "call_order": call_order,
                "employee_id": employee_id,
                "name": candidate["name"],
                "role": candidate["role"],
                "ml_score": ml_score,
                "outcome": outcome,
                "duration_seconds": duration,
            },
        })

        if outcome == "accepted":
            # Resolution: atomic update of incident + shift
            session = SessionLocal()
            try:
                inc = session.query(Incident).filter(Incident.id == incident_db_id).first()
                shft = session.query(Shift).filter(Shift.id == shift_id).first()
                inc.status = "resolved"
                inc.replacement_employee_id = employee_id
                inc.resolved_at = _now_utc()
                shft.assigned_employee_id = employee_id
                shft.status = "covered"
                session.commit()
            finally:
                session.close()

            await manager.broadcast({
                "type": "incident_resolved",
                "timestamp": _now_utc().isoformat(),
                "incident_id": incident.incident_id,
                "data": {
                    "replacement_employee_id": employee_id,
                    "replacement_name": candidate["name"],
                    "replacement_role": candidate["role"],
                    "total_calls": call_order,
                    "resolution_time_seconds": duration,
                },
            })
            resolved = True
            break

        # Result delay before next call: 1-3 seconds
        await asyncio.sleep(random.uniform(1.0, 3.0) * delay_multiplier)

    # If no one accepted -> escalate
    if not resolved:
        session = SessionLocal()
        try:
            inc = session.query(Incident).filter(Incident.id == incident_db_id).first()
            inc.status = "escalated"
            session.commit()
        finally:
            session.close()

        await manager.broadcast({
            "type": "incident_escalated",
            "timestamp": _now_utc().isoformat(),
            "incident_id": incident.incident_id,
            "data": {
                "reason": "All candidates exhausted",
                "total_calls": len(top_candidates),
            },
        })

    logger.info(
        f"Calling simulation complete for {incident.incident_id}: "
        f"{'resolved' if resolved else 'escalated'}"
    )
