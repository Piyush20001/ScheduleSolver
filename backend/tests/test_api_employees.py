"""Tests for /api/employees CRUD endpoints."""



def test_list_employees(client, seed_employees):
    """GET /api/employees returns 200 with list of seeded employees."""
    resp = client.get("/api/employees")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    # seed_employees inserts 3 active employees
    assert len(data) >= 3


def test_list_employees_filter_role(client, seed_employees):
    """GET /api/employees?role=server returns only servers."""
    resp = client.get("/api/employees", params={"role": "server"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    for emp in data:
        assert emp["role"] == "server"


def test_list_employees_filter_weekend(client, seed_employees):
    """GET /api/employees?weekend_available=true returns only weekend-available employees."""
    resp = client.get("/api/employees", params={"weekend_available": True})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    for emp in data:
        assert emp["weekend_available"] is True


def test_list_employees_filter_reliability(client, seed_employees):
    """GET /api/employees?min_reliability=0.8 returns only employees with reliability >= 0.8."""
    resp = client.get("/api/employees", params={"min_reliability": 0.8})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    for emp in data:
        assert emp["reliability_score"] >= 0.8


def test_create_employee(client):
    """POST /api/employees with valid body returns 201 with id."""
    body = {
        "name": "New Employee",
        "email": "new@example.com",
        "phone": "555-9999",
        "role": "host",
        "skill_level": 3,
        "reliability_score": 0.85,
        "prefers_morning": True,
        "prefers_evening": False,
        "weekend_available": True,
        "max_hours_weekly": 30,
        "is_active": True,
        "hired_date": "2026-01-15",
    }
    resp = client.post("/api/employees", json=body)
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert data["name"] == "New Employee"
    assert data["email"] == "new@example.com"
