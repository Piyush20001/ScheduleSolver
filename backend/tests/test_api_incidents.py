"""Tests for /api/incidents CRUD endpoints."""

import re


def test_list_incidents(client, seed_incidents):
    """GET /api/incidents returns 200 with enriched incidents."""
    resp = client.get("/api/incidents")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    for inc in data:
        assert "original_employee_name" in inc
        assert "shift_date" in inc
        assert "shift_type" in inc
        assert "role_required" in inc


def test_list_incidents_filter_status(client, seed_incidents):
    """GET /api/incidents?status=open returns only open incidents."""
    resp = client.get("/api/incidents", params={"status": "open"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    for inc in data:
        assert inc["status"] == "open"


def test_create_incident(client, seed_shifts):
    """POST /api/incidents creates incident with server-generated INC-XXX id."""
    body = {
        "shift_id": 1,
        "original_employee_id": 1,
        "reason": "sick",
        "urgency": "high",
    }
    resp = client.post("/api/incidents", json=body)
    assert resp.status_code == 201
    data = resp.json()
    assert "incident_id" in data
    assert re.match(r"INC-\d{3}", data["incident_id"])


def test_create_incident_auto_id(client, seed_shifts):
    """Two sequential POSTs generate INC-001 and INC-002."""
    body1 = {
        "shift_id": 1,
        "original_employee_id": 1,
        "reason": "sick",
        "urgency": "high",
    }
    resp1 = client.post("/api/incidents", json=body1)
    assert resp1.status_code == 201
    assert resp1.json()["incident_id"] == "INC-001"

    body2 = {
        "shift_id": 1,
        "original_employee_id": 1,
        "reason": "no_show",
        "urgency": "medium",
    }
    resp2 = client.post("/api/incidents", json=body2)
    assert resp2.status_code == 201
    assert resp2.json()["incident_id"] == "INC-002"


def test_docs_accessible(client):
    """GET /docs returns 200 (Swagger UI)."""
    resp = client.get("/docs")
    assert resp.status_code == 200
