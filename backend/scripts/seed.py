"""Database seeder for ScheduleSolver.

Populates the database with demo-ready data: ~25 employees, 2 weeks of
shifts (current + next week) with 5-8 open slots, and 3 pre-existing
incidents showing varied lifecycle stages.
"""

import datetime
import random

from app.ml.data_generator import SHIFT_DEFS, generate_employees
from app.models import CallLog, Employee, Incident, Shift


def seed_database(session):
    """Seed the database with demo data.

    Idempotent: skips seeding if employees already exist.

    Args:
        session: SQLAlchemy session.
    """
    # Idempotency check
    if session.query(Employee).count() > 0:
        print("[OK]   Database already seeded")
        return

    rng = random.Random(42)

    # --- 1. Seed employees ---
    employees_data = generate_employees()
    employees = []
    for emp_data in employees_data:
        emp = Employee(
            name=emp_data["name"],
            email=emp_data["email"],
            phone=emp_data["phone"],
            role=emp_data["role"],
            skill_level=emp_data["skill_level"],
            reliability_score=emp_data["reliability_score"],
            prefers_morning=emp_data["prefers_morning"],
            prefers_evening=emp_data["prefers_evening"],
            weekend_available=emp_data["weekend_available"],
            max_hours_weekly=emp_data["max_hours_weekly"],
            hired_date=emp_data["hired_date"],
        )
        employees.append(emp)
    session.add_all(employees)
    session.flush()  # Assign IDs

    # Build lookups
    emp_by_role = {}
    for emp in employees:
        emp_by_role.setdefault(emp.role, []).append(emp)
    all_employees = list(employees)

    # --- 2. Seed shifts for current week + next week ---
    today = datetime.date.today()
    # Find this week's Monday
    current_monday = today - datetime.timedelta(days=today.weekday())

    # Role distribution weights for shift demand
    role_weights = {
        "server": 4, "cook": 4, "cashier": 2,
        "barista": 2, "host": 2, "manager": 1,
    }
    role_pool = []
    for role, weight in role_weights.items():
        role_pool.extend([role] * weight)

    shifts = []
    shift_types = ["morning", "afternoon", "evening"]

    for week_offset in range(2):  # current week + next week
        week_monday = current_monday + datetime.timedelta(weeks=week_offset)
        for day_offset in range(7):
            shift_date = week_monday + datetime.timedelta(days=day_offset)
            is_weekend = shift_date.weekday() >= 5

            for shift_type in shift_types:
                shift_def = SHIFT_DEFS[shift_type]
                # Pick a role for this shift
                role_required = rng.choice(role_pool)

                shift = Shift(
                    date=shift_date,
                    start_time=shift_def["start"],
                    end_time=shift_def["end"],
                    shift_type=shift_type,
                    role_required=role_required,
                    min_skill_level=1,
                    is_weekend=is_weekend,
                    status="scheduled",
                    assigned_employee_id=None,
                )
                shifts.append(shift)

    session.add_all(shifts)
    session.flush()

    # Assign employees to most shifts, leave 5-8 open
    # Pick harder-to-fill slots for open shifts: early mornings, weekend evenings
    open_candidates = []
    for s in shifts:
        # Score how "hard to fill" this shift is
        hard_score = 0
        if s.shift_type == "morning":
            hard_score += 2
        if s.shift_type == "evening" and s.is_weekend:
            hard_score += 3
        if s.role_required in ("cook", "manager"):
            hard_score += 1
        open_candidates.append((hard_score, s))

    # Sort by hardness descending, pick 6 for open (middle of 5-8 range)
    open_candidates.sort(key=lambda x: (-x[0], x[1].id))
    num_open = 6
    open_shift_ids = set()
    for i in range(min(num_open, len(open_candidates))):
        open_shift_ids.add(open_candidates[i][1].id)
        open_candidates[i][1].status = "open"

    # Assign employees to non-open shifts
    # Compatible roles mapping
    compatible_roles = {
        "server": {"server", "general"},
        "cook": {"cook", "general"},
        "cashier": {"cashier", "general"},
        "barista": {"barista", "general"},
        "host": {"host", "general"},
        "manager": {"manager"},
    }

    for s in shifts:
        if s.id in open_shift_ids:
            continue
        # Find compatible employees, prefer matching role + high reliability
        compatible = compatible_roles.get(s.role_required, {s.role_required})
        candidates = [e for e in all_employees if e.role in compatible]
        if not candidates:
            candidates = [e for e in all_employees if e.role == "general"]
        if candidates:
            # Sort by reliability descending, pick top candidate with some randomness
            candidates.sort(key=lambda e: e.reliability_score, reverse=True)
            pick = candidates[rng.randint(0, min(2, len(candidates) - 1))]
            s.assigned_employee_id = pick.id
            s.status = "scheduled"

    session.flush()

    # --- 3. Seed 3 pre-existing incidents ---
    now = datetime.datetime.now(datetime.timezone.utc)
    open_shifts_list = [s for s in shifts if s.status == "open"]

    # Incident 1: Critical, Open (unresolved sick call)
    # Pick an open morning cook shift (or first open shift)
    inc1_shift = None
    for s in open_shifts_list:
        if s.shift_type == "morning" and s.role_required == "cook":
            inc1_shift = s
            break
    if inc1_shift is None:
        inc1_shift = open_shifts_list[0]

    # Find a reliable cook as the "original employee"
    cooks = emp_by_role.get("cook", [])
    reliable_cook = max(cooks, key=lambda e: e.reliability_score) if cooks else all_employees[0]

    incident_1 = Incident(
        incident_id="INC-001",
        shift_id=inc1_shift.id,
        original_employee_id=reliable_cook.id,
        reason="Sick call",
        urgency="critical",
        status="open",
        created_at=now - datetime.timedelta(minutes=30),
    )
    session.add(incident_1)
    session.flush()

    # Incident 2: Medium, In-Progress (2 calls already made)
    inc2_shift = None
    for s in open_shifts_list:
        if s.shift_type == "afternoon" and s.id != inc1_shift.id:
            inc2_shift = s
            break
    if inc2_shift is None:
        for s in open_shifts_list:
            if s.id != inc1_shift.id:
                inc2_shift = s
                break
    if inc2_shift is None:
        inc2_shift = open_shifts_list[-1]

    # Find an employee for original
    servers = emp_by_role.get("server", [])
    original_server = servers[0] if servers else all_employees[1]

    incident_2 = Incident(
        incident_id="INC-002",
        shift_id=inc2_shift.id,
        original_employee_id=original_server.id,
        reason="No show",
        urgency="medium",
        status="in_progress",
        created_at=now - datetime.timedelta(hours=1),
    )
    session.add(incident_2)
    session.flush()

    # Call logs for incident 2
    call_log_2a = CallLog(
        incident_id=incident_2.id,
        employee_id=all_employees[2].id,
        call_order=1,
        status="declined",
        ml_score=0.82,
        call_started_at=now - datetime.timedelta(minutes=55),
        call_ended_at=now - datetime.timedelta(minutes=54),
        duration_seconds=15,
    )
    call_log_2b = CallLog(
        incident_id=incident_2.id,
        employee_id=all_employees[3].id,
        call_order=2,
        status="no_answer",
        ml_score=0.74,
        call_started_at=now - datetime.timedelta(minutes=50),
        call_ended_at=now - datetime.timedelta(minutes=49),
        duration_seconds=20,
    )
    session.add_all([call_log_2a, call_log_2b])

    # Incident 3: Low, Resolved (complete lifecycle)
    # Find a scheduled shift from earlier this week or yesterday
    yesterday = today - datetime.timedelta(days=1)
    inc3_shift = None
    for s in shifts:
        if s.status == "scheduled" and s.date <= yesterday and s.assigned_employee_id:
            inc3_shift = s
            break
    # If no past shifts, use any scheduled shift
    if inc3_shift is None:
        for s in shifts:
            if s.status == "scheduled" and s.assigned_employee_id:
                inc3_shift = s
                break
    if inc3_shift is None:
        inc3_shift = shifts[0]

    # Find the replacement employee (someone who accepted)
    replacement_emp = None
    for emp in all_employees:
        if emp.id != inc3_shift.assigned_employee_id:
            replacement_emp = emp
            break
    if replacement_emp is None:
        replacement_emp = all_employees[-1]

    resolved_at = now - datetime.timedelta(hours=23, minutes=55)
    incident_3 = Incident(
        incident_id="INC-003",
        shift_id=inc3_shift.id,
        original_employee_id=inc3_shift.assigned_employee_id or all_employees[4].id,
        reason="Schedule conflict",
        urgency="low",
        status="resolved",
        replacement_employee_id=replacement_emp.id,
        created_at=now - datetime.timedelta(hours=24),
        resolved_at=resolved_at,
    )
    session.add(incident_3)
    session.flush()

    # Call logs for incident 3 (3 calls, last one accepted)
    call_log_3a = CallLog(
        incident_id=incident_3.id,
        employee_id=all_employees[5].id,
        call_order=1,
        status="no_answer",
        ml_score=0.88,
        call_started_at=now - datetime.timedelta(hours=24),
        call_ended_at=now - datetime.timedelta(hours=23, minutes=59),
        duration_seconds=25,
    )
    call_log_3b = CallLog(
        incident_id=incident_3.id,
        employee_id=all_employees[6].id,
        call_order=2,
        status="declined",
        ml_score=0.76,
        call_started_at=now - datetime.timedelta(hours=23, minutes=58),
        call_ended_at=now - datetime.timedelta(hours=23, minutes=57),
        duration_seconds=12,
    )
    call_log_3c = CallLog(
        incident_id=incident_3.id,
        employee_id=replacement_emp.id,
        call_order=3,
        status="accepted",
        ml_score=0.71,
        call_started_at=now - datetime.timedelta(hours=23, minutes=56),
        call_ended_at=now - datetime.timedelta(hours=23, minutes=55),
        duration_seconds=18,
    )
    session.add_all([call_log_3a, call_log_3b, call_log_3c])

    session.commit()

    shift_count = session.query(Shift).count()
    print(f"[OK]   Database ready: {len(employees)} employees, {shift_count} shifts, 3 incidents")
