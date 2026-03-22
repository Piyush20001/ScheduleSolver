"""Tests for /api/shifts CRUD endpoints."""



def test_list_shifts(client, seed_shifts):
    """GET /api/shifts returns 200 with shifts including assigned_employee_name."""
    resp = client.get("/api/shifts")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 2


def test_list_shifts_date_filter(client, seed_shifts):
    """GET /api/shifts?start_date=...&end_date=... returns filtered shifts."""
    resp = client.get(
        "/api/shifts",
        params={"start_date": "2026-03-16", "end_date": "2026-03-17"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    for shift in data:
        assert "2026-03-16" <= shift["date"] <= "2026-03-17"


def test_create_shift(client, seed_employees):
    """POST /api/shifts with valid body returns 201."""
    body = {
        "date": "2026-03-20",
        "start_time": "06:00",
        "end_time": "14:00",
        "shift_type": "morning",
        "role_required": "server",
        "min_skill_level": 1,
        "is_weekend": False,
        "status": "scheduled",
    }
    resp = client.post("/api/shifts", json=body)
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data


def test_shift_enrichment(client, seed_shifts):
    """Shifts with assigned_employee_id have assigned_employee_name populated, unassigned shifts have null."""
    resp = client.get("/api/shifts")
    data = resp.json()
    found_assigned = False
    found_unassigned = False
    for shift in data:
        if shift.get("assigned_employee_id") is not None:
            assert shift["assigned_employee_name"] is not None
            assert isinstance(shift["assigned_employee_name"], str)
            found_assigned = True
        else:
            assert shift["assigned_employee_name"] is None
            found_unassigned = True
    assert found_assigned, "Expected at least one assigned shift in seed data"
    assert found_unassigned, "Expected at least one unassigned shift in seed data"
