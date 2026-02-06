"""SQLAlchemy ORM models for ScheduleSolver (4 tables)."""

from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100), unique=True)
    phone: Mapped[str] = mapped_column(String(20))
    role: Mapped[str] = mapped_column(String(50))
    skill_level: Mapped[int] = mapped_column(Integer, default=1)
    reliability_score: Mapped[float] = mapped_column(Float, default=0.7)
    prefers_morning: Mapped[bool] = mapped_column(Boolean, default=False)
    prefers_evening: Mapped[bool] = mapped_column(Boolean, default=False)
    weekend_available: Mapped[bool] = mapped_column(Boolean, default=False)
    max_hours_weekly: Mapped[int] = mapped_column(Integer, default=40)
    hours_worked_this_week: Mapped[float] = mapped_column(Float, default=0.0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    hired_date: Mapped[date] = mapped_column(Date)


class Shift(Base):
    __tablename__ = "shifts"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date] = mapped_column(Date)
    start_time: Mapped[str] = mapped_column(String(5))   # e.g. "06:00"
    end_time: Mapped[str] = mapped_column(String(5))     # e.g. "14:00"
    shift_type: Mapped[str] = mapped_column(String(20))  # morning/afternoon/evening
    role_required: Mapped[str] = mapped_column(String(50))
    min_skill_level: Mapped[int] = mapped_column(Integer, default=1)
    is_weekend: Mapped[bool] = mapped_column(Boolean, default=False)
    assigned_employee_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("employees.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(20), default="scheduled"
    )  # scheduled/open/covered/cancelled


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(primary_key=True)
    incident_id: Mapped[str] = mapped_column(String(20), unique=True)  # e.g. "INC-001"
    shift_id: Mapped[int] = mapped_column(ForeignKey("shifts.id"))
    original_employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))
    reason: Mapped[str] = mapped_column(String(50))
    urgency: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(
        String(20), default="open"
    )  # open/in_progress/resolved/escalated
    replacement_employee_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("employees.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class CallLog(Base):
    __tablename__ = "call_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    incident_id: Mapped[int] = mapped_column(ForeignKey("incidents.id"))
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))
    call_order: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(
        String(20)
    )  # accepted/declined/no_answer/voicemail
    ml_score: Mapped[float] = mapped_column(Float)
    call_started_at: Mapped[datetime] = mapped_column(DateTime)
    call_ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
