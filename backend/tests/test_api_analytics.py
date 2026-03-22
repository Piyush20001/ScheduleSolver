"""Tests for GET /api/analytics/* endpoints."""

from datetime import date, datetime, timezone
from unittest.mock import patch

import pytest

from app.models import CallLog, Employee, Incident, Shift


# Mock metrics for model-info tests
MOCK_METRICS = {
    "roc_auc": 0.984,
    "accuracy": 0.96,
    "precision": 0.95,
    "recall": 0.97,
    "confusion_matrix": {"tn": 100, "fp": 5, "fn": 3, "tp": 92},
    "feature_importances": {
        "preference_match": 0.35,
        "reliability_score": 0.25,
        "hours_remaining": 0.15,
        "role_match": 0.10,
        "skill_gap": 0.08,
        "is_weekend_match": 0.05,
        "days_since_last_shift": 0.02,
    },
    "train_weeks": "1-10",
    "test_weeks": "11-12",
}


@pytest.fixture
def seed_analytics_data(client):
    """Seed employees, shifts, incidents, and call_logs for analytics tests."""
    from tests.conftest import _get_seed_session

    db = _get_seed_session()
    try:
        # Employees
        emp1 = Employee(
            name="Ana Analyst",
            email="ana@analytics.com",
            phone="555-2001",
            role="server",
            skill_level=4,
            reliability_score=0.90,
            prefers_morning=True,
            prefers_evening=False,
            weekend_available=True,
            max_hours_weekly=35,
            hours_worked_this_week=10.0,
            is_active=True,
            hired_date=date(2024, 1, 15),
        )
        emp2 = Employee(
            name="Ben Benchmarks",
            email="ben@analytics.com",
            phone="555-2002",
            role="cook",
            skill_level=3,
            reliability_score=0.80,
            prefers_morning=False,
            prefers_evening=True,
            weekend_available=False,
            max_hours_weekly=30,
            hours_worked_this_week=5.0,
            is_active=True,
            hired_date=date(2024, 6, 1),
        )
        db.add_all([emp1, emp2])
        db.commit()

        # Shifts
        shift1 = Shift(
            date=date(2026, 3, 16),
            start_time="06:00",
            end_time="14:00",
            shift_type="morning",
            role_required="server",
            min_skill_level=2,
            is_weekend=False,
            assigned_employee_id=1,
            status="scheduled",
        )
        shift2 = Shift(
            date=date(2026, 3, 17),
            start_time="14:00",
            end_time="22:00",
            shift_type="evening",
            role_required="cook",
            min_skill_level=1,
            is_weekend=False,
            assigned_employee_id=None,
            status="open",
        )
        db.add_all([shift1, shift2])
        db.commit()

        # Incidents (1 resolved with call_logs, 1 open)
        inc1 = Incident(
            incident_id="INC-001",
            shift_id=1,
            original_employee_id=1,
            reason="sick",
            urgency="high",
            status="resolved",
            created_at=datetime(2026, 3, 16, 5, 0, tzinfo=timezone.utc),
            resolved_at=datetime(2026, 3, 16, 5, 30, tzinfo=timezone.utc),
        )
        inc2 = Incident(
            incident_id="INC-002",
            shift_id=2,
            original_employee_id=2,
            reason="no_show",
            urgency="medium",
            status="open",
            created_at=datetime(2026, 3, 17, 13, 0, tzinfo=timezone.utc),
        )
        db.add_all([inc1, inc2])
        db.commit()

        # CallLogs for INC-001 (3 calls: declined, no_answer, accepted)
        calls = [
            CallLog(
                incident_id=1,
                employee_id=2,
                call_order=1,
                status="declined",
                ml_score=0.85,
                call_started_at=datetime(2026, 3, 16, 5, 5, tzinfo=timezone.utc),
                call_ended_at=datetime(2026, 3, 16, 5, 10, tzinfo=timezone.utc),
            ),
            CallLog(
                incident_id=1,
                employee_id=1,
                call_order=2,
                status="no_answer",
                ml_score=0.78,
                call_started_at=datetime(2026, 3, 16, 5, 10, tzinfo=timezone.utc),
                call_ended_at=datetime(2026, 3, 16, 5, 15, tzinfo=timezone.utc),
            ),
            CallLog(
                incident_id=1,
                employee_id=1,
                call_order=3,
                status="accepted",
                ml_score=0.78,
                call_started_at=datetime(2026, 3, 16, 5, 20, tzinfo=timezone.utc),
                call_ended_at=datetime(2026, 3, 16, 5, 25, tzinfo=timezone.utc),
            ),
        ]
        db.add_all(calls)
        db.commit()

        return {"employees": [emp1, emp2], "incidents": [inc1, inc2], "calls": calls}
    finally:
        db.close()


class TestModelInfo:
    """Tests for GET /api/analytics/model-info."""

    def test_model_info(self, client):
        """Returns roc_auc, accuracy, precision, recall, feature_importances."""
        with patch(
            "app.routers.analytics.ml_service.get_metrics",
            return_value=MOCK_METRICS,
        ):
            resp = client.get("/api/analytics/model-info")

        assert resp.status_code == 200
        data = resp.json()
        assert data["roc_auc"] == 0.984
        assert data["accuracy"] == 0.96
        assert data["precision"] == 0.95
        assert data["recall"] == 0.97
        assert "feature_importances" in data
        assert data["feature_importances"]["preference_match"] == 0.35


class TestCoverageStats:
    """Tests for GET /api/analytics/coverage-stats."""

    def test_coverage_stats(self, client, seed_analytics_data):
        """Returns computed stats from call_logs."""
        resp = client.get("/api/analytics/coverage-stats")
        assert resp.status_code == 200
        data = resp.json()

        # 2 total incidents, 1 resolved => resolution_rate = 50.0%
        assert data["resolution_rate_percent"] == 50.0

        # Resolved incident INC-001 has 3 call_logs => avg_calls_to_resolution = 3.0
        assert data["avg_calls_to_resolution"] == 3.0

        # INC-001 resolved_at - created_at = 30 minutes = 1800 seconds
        assert data["avg_time_to_cover_seconds"] == 1800.0

    def test_coverage_stats_empty(self, client):
        """coverage-stats with no data returns zeros (not 500 error)."""
        resp = client.get("/api/analytics/coverage-stats")
        assert resp.status_code == 200
        data = resp.json()
        assert data["avg_calls_to_resolution"] == 0.0
        assert data["resolution_rate_percent"] == 0.0
        assert data["avg_time_to_cover_seconds"] == 0.0


class TestEmployeePerformance:
    """Tests for GET /api/analytics/employee-performance."""

    def test_employee_performance(self, client, seed_analytics_data):
        """Returns employees sorted by acceptance_rate descending."""
        resp = client.get("/api/analytics/employee-performance")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2  # 2 seeded employees
        # Sorted by acceptance_rate descending
        rates = [e["acceptance_rate"] for e in data]
        assert rates == sorted(rates, reverse=True)

    def test_employee_performance_with_calls(self, client, seed_analytics_data):
        """Employee with 2 accepted / 3 total shows acceptance_rate of 0.667."""
        resp = client.get("/api/analytics/employee-performance")
        assert resp.status_code == 200
        data = resp.json()

        # emp1 (Ana): has 2 calls (1 no_answer, 1 accepted) => 1 accepted / 2 total = 0.5
        # emp2 (Ben): has 1 call (1 declined) => 0 accepted / 1 total = 0.0
        ana = next(e for e in data if e["name"] == "Ana Analyst")
        assert ana["total_calls"] == 2
        assert ana["accepted_calls"] == 1
        assert ana["acceptance_rate"] == 0.5

        ben = next(e for e in data if e["name"] == "Ben Benchmarks")
        assert ben["total_calls"] == 1
        assert ben["accepted_calls"] == 0
        assert ben["acceptance_rate"] == 0.0
