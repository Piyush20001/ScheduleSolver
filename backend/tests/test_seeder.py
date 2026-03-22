"""Tests for database seeder (DATA-01, DATA-02, DATA-03)."""

import datetime


from app.models import CallLog, Employee, Incident, Shift
from scripts.seed import seed_database


class TestSeeder:
    """Database seeding tests."""

    def test_employee_seeding(self, test_db):
        """DATA-01: Seeds ~25 employees with correct names, roles, reliability."""
        seed_database(test_db)
        employees = test_db.query(Employee).all()
        assert 20 <= len(employees) <= 30, f"Expected ~25, got {len(employees)}"
        # Check expected roles exist
        roles = {e.role for e in employees}
        assert "cook" in roles
        assert "server" in roles
        assert "manager" in roles

    def test_shift_seeding(self, test_db):
        """DATA-02: Seeds shifts for current + next week with 5-8 open."""
        seed_database(test_db)
        shifts = test_db.query(Shift).all()
        assert len(shifts) > 0, "No shifts seeded"
        open_shifts = [s for s in shifts if s.status == "open"]
        assert 5 <= len(open_shifts) <= 8, (
            f"Expected 5-8 open shifts, got {len(open_shifts)}"
        )

    def test_shift_dates_relative(self, test_db):
        """DATA-02: All shift dates are relative to today (not hardcoded)."""
        seed_database(test_db)
        today = datetime.date.today()
        shifts = test_db.query(Shift).all()
        for s in shifts:
            diff = abs((s.date - today).days)
            assert diff <= 14, (
                f"Shift date {s.date} is {diff} days from today, expected <= 14"
            )

    def test_incident_seeding(self, test_db):
        """DATA-03: 3 incidents with correct statuses and urgencies."""
        seed_database(test_db)
        incidents = test_db.query(Incident).all()
        assert len(incidents) == 3, f"Expected 3, got {len(incidents)}"
        # Check each incident type
        statuses = {i.status for i in incidents}
        assert "open" in statuses
        assert "in_progress" in statuses
        assert "resolved" in statuses
        urgencies = {i.urgency for i in incidents}
        assert "critical" in urgencies
        assert "medium" in urgencies
        assert "low" in urgencies

    def test_resolved_incident_has_call_logs(self, test_db):
        """DATA-03: In-progress and resolved incidents have call_log entries."""
        seed_database(test_db)
        # In-progress incident should have ~2 call logs
        in_progress = test_db.query(Incident).filter_by(status="in_progress").first()
        assert in_progress is not None
        ip_logs = test_db.query(CallLog).filter_by(incident_id=in_progress.id).all()
        assert len(ip_logs) >= 2, f"In-progress has {len(ip_logs)} logs, expected >= 2"

        # Resolved incident should have call logs ending with accepted
        resolved = test_db.query(Incident).filter_by(status="resolved").first()
        assert resolved is not None
        r_logs = test_db.query(CallLog).filter_by(incident_id=resolved.id).order_by(CallLog.call_order).all()
        assert len(r_logs) >= 2, f"Resolved has {len(r_logs)} logs, expected >= 2"
        assert r_logs[-1].status == "accepted", f"Last call log is {r_logs[-1].status}, expected accepted"

    def test_idempotent_seed(self, test_db):
        """Calling seed_database twice does not duplicate data."""
        seed_database(test_db)
        count_1 = test_db.query(Employee).count()
        seed_database(test_db)
        count_2 = test_db.query(Employee).count()
        assert count_1 == count_2, f"Employee count changed: {count_1} -> {count_2}"
