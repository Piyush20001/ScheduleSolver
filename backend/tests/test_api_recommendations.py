"""Tests for POST /api/recommendations/rank endpoint."""

from datetime import date
from unittest.mock import patch

import pytest

from app.models import Employee, Shift


@pytest.fixture
def seed_rank_data(client):
    """Seed employees and an open shift for ranking tests."""
    from tests.conftest import _get_seed_session

    db = _get_seed_session()
    try:
        employees = [
            Employee(
                name="Alice Server",
                email="alice@rank.com",
                phone="555-1001",
                role="server",
                skill_level=4,
                reliability_score=0.92,
                prefers_morning=True,
                prefers_evening=False,
                weekend_available=True,
                max_hours_weekly=35,
                hours_worked_this_week=10.0,
                is_active=True,
                hired_date=date(2024, 1, 15),
            ),
            Employee(
                name="Bob Cook",
                email="bob@rank.com",
                phone="555-1002",
                role="cook",
                skill_level=3,
                reliability_score=0.75,
                prefers_morning=False,
                prefers_evening=True,
                weekend_available=False,
                max_hours_weekly=30,
                hours_worked_this_week=15.0,
                is_active=True,
                hired_date=date(2024, 6, 1),
            ),
            Employee(
                name="Carol General",
                email="carol@rank.com",
                phone="555-1003",
                role="general",
                skill_level=2,
                reliability_score=0.70,
                prefers_morning=True,
                prefers_evening=False,
                weekend_available=True,
                max_hours_weekly=30,
                hours_worked_this_week=5.0,
                is_active=True,
                hired_date=date(2025, 3, 1),
            ),
        ]
        db.add_all(employees)
        db.commit()

        shift = Shift(
            date=date(2026, 3, 20),
            start_time="06:00",
            end_time="14:00",
            shift_type="morning",
            role_required="server",
            min_skill_level=2,
            is_weekend=False,
            assigned_employee_id=None,
            status="open",
        )
        db.add(shift)
        db.commit()

        return {"employees": employees, "shift": shift}
    finally:
        db.close()


def _mock_rank_candidates(shift, employees):
    """Mock rank_candidates that returns deterministic scores with reasons."""
    results = []
    for i, emp in enumerate(employees):
        score = round(0.95 - i * 0.1, 4)
        results.append({
            "employee_id": emp.id,
            "name": emp.name,
            "role": emp.role,
            "score": score,
            "reason": "Strong preference match, High reliability (0.92), Exact role match",
        })
    results.sort(key=lambda x: x["score"], reverse=True)
    return results


class TestRankCandidates:
    """Tests for POST /api/recommendations/rank."""

    def test_rank_candidates_returns_sorted(self, client, seed_rank_data):
        """POST /rank returns candidates sorted by score descending."""
        with patch(
            "app.routers.recommendations.ml_service.rank_candidates",
            side_effect=_mock_rank_candidates,
        ):
            resp = client.post("/api/recommendations/rank", json={"shift_id": 1})

        assert resp.status_code == 200
        data = resp.json()
        candidates = data["candidates"]
        assert len(candidates) > 0
        scores = [c["score"] for c in candidates]
        assert scores == sorted(scores, reverse=True)

    def test_rank_candidates_has_reasons(self, client, seed_rank_data):
        """Each candidate in response has a non-empty reason string."""
        with patch(
            "app.routers.recommendations.ml_service.rank_candidates",
            side_effect=_mock_rank_candidates,
        ):
            resp = client.post("/api/recommendations/rank", json={"shift_id": 1})

        assert resp.status_code == 200
        for c in resp.json()["candidates"]:
            assert isinstance(c["reason"], str)
            assert len(c["reason"]) > 0

    def test_rank_candidates_reason_format(self, client, seed_rank_data):
        """Reason strings contain comma-separated phrases (top 3 feature highlights)."""
        with patch(
            "app.routers.recommendations.ml_service.rank_candidates",
            side_effect=_mock_rank_candidates,
        ):
            resp = client.post("/api/recommendations/rank", json={"shift_id": 1})

        assert resp.status_code == 200
        for c in resp.json()["candidates"]:
            phrases = [p.strip() for p in c["reason"].split(",")]
            assert len(phrases) == 3, f"Expected 3 phrases, got {len(phrases)}: {c['reason']}"

    def test_rank_candidates_includes_name_role(self, client, seed_rank_data):
        """Each candidate has employee_id, name, role, score fields."""
        with patch(
            "app.routers.recommendations.ml_service.rank_candidates",
            side_effect=_mock_rank_candidates,
        ):
            resp = client.post("/api/recommendations/rank", json={"shift_id": 1})

        assert resp.status_code == 200
        data = resp.json()
        assert data["shift_id"] == 1
        assert data["role_required"] == "server"
        for c in data["candidates"]:
            assert "employee_id" in c
            assert "name" in c
            assert "role" in c
            assert "score" in c

    def test_rank_candidates_invalid_shift(self, client, seed_rank_data):
        """POST with non-existent shift_id returns 404."""
        resp = client.post("/api/recommendations/rank", json={"shift_id": 9999})
        assert resp.status_code == 404

    def test_rank_candidates_filters_compatible(self, client, seed_rank_data):
        """Only employees with compatible roles appear in results."""
        with patch(
            "app.routers.recommendations.ml_service.rank_candidates",
            side_effect=_mock_rank_candidates,
        ):
            resp = client.post("/api/recommendations/rank", json={"shift_id": 1})

        assert resp.status_code == 200
        data = resp.json()
        # Shift requires "server" role. Compatible: server, general.
        # Bob (cook) should NOT appear.
        candidate_names = [c["name"] for c in data["candidates"]]
        assert "Bob Cook" not in candidate_names
        # Alice (server) and Carol (general) should appear
        assert "Alice Server" in candidate_names
        assert "Carol General" in candidate_names
