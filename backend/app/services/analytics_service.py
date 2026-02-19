"""Analytics service: coverage stats and employee performance queries.

Computes real-time analytics from database records -- no caching,
always reflects current state.
"""

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import CallLog, Employee, Incident


def get_coverage_stats(db: Session) -> dict:
    """Compute coverage statistics from incidents and call logs.

    Returns:
        Dict with avg_calls_to_resolution, resolution_rate_percent,
        avg_time_to_cover_seconds. All default to 0.0 when no data exists.
    """
    # Total and resolved incident counts
    total_incidents = db.query(func.count(Incident.id)).scalar() or 0
    resolved_incidents = (
        db.query(func.count(Incident.id))
        .filter(Incident.status == "resolved")
        .scalar()
        or 0
    )

    # Resolution rate
    if total_incidents > 0:
        resolution_rate = round(resolved_incidents / total_incidents * 100, 1)
    else:
        resolution_rate = 0.0

    # Average calls to resolution (count call_logs per resolved incident)
    avg_calls = 0.0
    avg_time = 0.0

    if resolved_incidents > 0:
        # Get resolved incident IDs
        resolved_ids = (
            db.query(Incident.id).filter(Incident.status == "resolved").all()
        )
        resolved_id_list = [r[0] for r in resolved_ids]

        # Count call_logs per resolved incident and average
        total_calls_for_resolved = (
            db.query(func.count(CallLog.id))
            .filter(CallLog.incident_id.in_(resolved_id_list))
            .scalar()
            or 0
        )
        avg_calls = round(total_calls_for_resolved / resolved_incidents, 1)

        # Average time to cover (resolved_at - created_at) in seconds
        resolved_records = (
            db.query(Incident)
            .filter(Incident.status == "resolved", Incident.resolved_at.isnot(None))
            .all()
        )
        if resolved_records:
            total_seconds = 0.0
            count = 0
            for inc in resolved_records:
                delta = (inc.resolved_at - inc.created_at).total_seconds()
                total_seconds += delta
                count += 1
            avg_time = round(total_seconds / count, 1) if count > 0 else 0.0

    return {
        "avg_calls_to_resolution": avg_calls,
        "resolution_rate_percent": resolution_rate,
        "avg_time_to_cover_seconds": avg_time,
    }


def get_employee_performance(db: Session) -> list[dict]:
    """Compute employee performance based on call log acceptance rates.

    Returns:
        List of dicts sorted by acceptance_rate descending:
        [{employee_id, name, role, total_calls, accepted_calls, acceptance_rate}, ...]
    """
    employees = db.query(Employee).all()
    results = []

    for emp in employees:
        total_calls = (
            db.query(func.count(CallLog.id))
            .filter(CallLog.employee_id == emp.id)
            .scalar()
            or 0
        )
        accepted_calls = (
            db.query(func.count(CallLog.id))
            .filter(CallLog.employee_id == emp.id, CallLog.status == "accepted")
            .scalar()
            or 0
        )
        acceptance_rate = round(accepted_calls / total_calls, 3) if total_calls > 0 else 0.0

        results.append({
            "employee_id": emp.id,
            "name": emp.name,
            "role": emp.role,
            "total_calls": total_calls,
            "accepted_calls": accepted_calls,
            "acceptance_rate": acceptance_rate,
        })

    # Sort by acceptance_rate descending
    results.sort(key=lambda x: x["acceptance_rate"], reverse=True)
    return results
