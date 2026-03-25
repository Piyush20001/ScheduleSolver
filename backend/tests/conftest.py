"""Shared test fixtures for ScheduleSolver v2."""

# WORKAROUND: Python 3.14 + Windows WMI hang in platform.machine()
# SQLAlchemy's compat.py calls platform.machine() on import, which triggers
# a WMI query that hangs indefinitely on Python 3.14 / Windows 11.
# Patch before any SQLAlchemy import.
import platform as _platform
import sys as _sys

if _sys.platform == "win32" and _sys.version_info >= (3, 14):
    _platform.machine = lambda: "AMD64"

import shutil
import tempfile
from datetime import date, datetime, timezone
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models import CallLog, Employee, Incident, Shift  # noqa: F401 -- register models


@pytest.fixture
def test_db():
    """In-memory SQLite session for testing. Creates tables, yields session, drops after."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def tmp_model_dir():
    """Temporary directory for model.pkl and metrics.json artifacts."""
    dirpath = tempfile.mkdtemp(prefix="ss_model_")
    yield dirpath
    shutil.rmtree(dirpath, ignore_errors=True)


# Shared engine for API tests -- StaticPool ensures single in-memory DB
_test_engine = None
_TestSession = None


@pytest.fixture
def client():
    """TestClient with in-memory SQLite database dependency override.

    Uses StaticPool so all connections share the same in-memory database.
    Also patches SessionLocal in the calling_service module so the background
    calling simulation shares the same in-memory DB.
    """
    global _test_engine, _TestSession
    _test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=_test_engine)
    _TestSession = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)

    def override_get_db():
        db = _TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    # Patch SessionLocal in calling_service and agent_service so they use the same in-memory DB
    with patch("app.services.calling_service.SessionLocal", _TestSession), \
         patch("app.services.agent_service.SessionLocal", _TestSession):
        with TestClient(app) as tc:
            yield tc

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=_test_engine)
    _test_engine = None
    _TestSession = None


def _get_seed_session():
    """Get a session from the shared test engine for seeding data."""
    db = _TestSession()
    return db


@pytest.fixture
def seed_employees(client):
    """Insert 3 test employees with varying roles and reliabilities."""
    db = _get_seed_session()
    try:
        employees = [
            Employee(
                name="Alice Manager",
                email="alice@test.com",
                phone="555-0001",
                role="server",
                skill_level=5,
                reliability_score=0.92,
                prefers_morning=True,
                prefers_evening=False,
                weekend_available=True,
                max_hours_weekly=40,
                hours_worked_this_week=20.0,
                is_active=True,
                hired_date=date(2024, 1, 15),
            ),
            Employee(
                name="Bob Bartender",
                email="bob@test.com",
                phone="555-0002",
                role="barista",
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
                name="Carol Server",
                email="carol@test.com",
                phone="555-0003",
                role="server",
                skill_level=4,
                reliability_score=0.88,
                prefers_morning=True,
                prefers_evening=True,
                weekend_available=True,
                max_hours_weekly=35,
                hours_worked_this_week=10.0,
                is_active=True,
                hired_date=date(2025, 2, 10),
            ),
        ]
        db.add_all(employees)
        db.commit()
        return employees
    finally:
        db.close()


@pytest.fixture
def seed_shifts(client, seed_employees):
    """Insert test shifts -- some assigned, some unassigned."""
    db = _get_seed_session()
    try:
        shifts = [
            Shift(
                date=date(2026, 3, 16),
                start_time="06:00",
                end_time="14:00",
                shift_type="morning",
                role_required="server",
                min_skill_level=2,
                is_weekend=False,
                assigned_employee_id=1,  # Alice
                status="scheduled",
            ),
            Shift(
                date=date(2026, 3, 17),
                start_time="14:00",
                end_time="22:00",
                shift_type="evening",
                role_required="barista",
                min_skill_level=1,
                is_weekend=False,
                assigned_employee_id=None,  # Unassigned
                status="open",
            ),
            Shift(
                date=date(2026, 3, 20),
                start_time="06:00",
                end_time="14:00",
                shift_type="morning",
                role_required="server",
                min_skill_level=1,
                is_weekend=False,
                assigned_employee_id=3,  # Carol
                status="scheduled",
            ),
        ]
        db.add_all(shifts)
        db.commit()
        return shifts
    finally:
        db.close()


@pytest.fixture
def seed_incidents(client, seed_shifts):
    """Insert test incidents linked to seeded shifts and employees."""
    db = _get_seed_session()
    try:
        incidents = [
            Incident(
                incident_id="INC-001",
                shift_id=1,
                original_employee_id=1,
                reason="sick",
                urgency="high",
                status="open",
                created_at=datetime(2026, 3, 16, 5, 0, tzinfo=timezone.utc),
            ),
            Incident(
                incident_id="INC-002",
                shift_id=2,
                original_employee_id=2,
                reason="no_show",
                urgency="medium",
                status="resolved",
                created_at=datetime(2026, 3, 17, 13, 0, tzinfo=timezone.utc),
                resolved_at=datetime(2026, 3, 17, 14, 0, tzinfo=timezone.utc),
            ),
        ]
        db.add_all(incidents)
        db.commit()
        return incidents
    finally:
        db.close()


@pytest.fixture
def seed_for_simulation(client):
    """Seed data for calling simulation tests: 5 employees + 1 open shift."""
    db = _get_seed_session()
    try:
        employees = [
            Employee(
                name="Emp High1",
                email="h1@test.com",
                phone="555-1001",
                role="server",
                skill_level=5,
                reliability_score=0.95,
                prefers_morning=True,
                prefers_evening=False,
                weekend_available=True,
                max_hours_weekly=40,
                hours_worked_this_week=10.0,
                is_active=True,
                hired_date=date(2024, 1, 1),
            ),
            Employee(
                name="Emp High2",
                email="h2@test.com",
                phone="555-1002",
                role="server",
                skill_level=4,
                reliability_score=0.90,
                prefers_morning=True,
                prefers_evening=True,
                weekend_available=True,
                max_hours_weekly=40,
                hours_worked_this_week=15.0,
                is_active=True,
                hired_date=date(2024, 2, 1),
            ),
            Employee(
                name="Emp Med1",
                email="m1@test.com",
                phone="555-1003",
                role="server",
                skill_level=3,
                reliability_score=0.70,
                prefers_morning=False,
                prefers_evening=True,
                weekend_available=False,
                max_hours_weekly=35,
                hours_worked_this_week=20.0,
                is_active=True,
                hired_date=date(2024, 3, 1),
            ),
            Employee(
                name="Emp Low1",
                email="l1@test.com",
                phone="555-1004",
                role="server",
                skill_level=2,
                reliability_score=0.45,
                prefers_morning=False,
                prefers_evening=False,
                weekend_available=False,
                max_hours_weekly=30,
                hours_worked_this_week=25.0,
                is_active=True,
                hired_date=date(2024, 4, 1),
            ),
            Employee(
                name="Emp Original",
                email="orig@test.com",
                phone="555-1005",
                role="server",
                skill_level=4,
                reliability_score=0.85,
                prefers_morning=True,
                prefers_evening=False,
                weekend_available=True,
                max_hours_weekly=40,
                hours_worked_this_week=30.0,
                is_active=True,
                hired_date=date(2024, 5, 1),
            ),
        ]
        db.add_all(employees)
        db.flush()

        shift = Shift(
            date=date(2026, 3, 25),
            start_time="06:00",
            end_time="14:00",
            shift_type="morning",
            role_required="server",
            min_skill_level=1,
            is_weekend=False,
            assigned_employee_id=employees[4].id,  # Emp Original
            status="scheduled",
        )
        db.add(shift)
        db.commit()

        return {
            "shift_id": shift.id,
            "original_employee_id": employees[4].id,
            "employee_ids": [e.id for e in employees[:4]],  # 4 candidates (excluding original)
        }
    finally:
        db.close()
