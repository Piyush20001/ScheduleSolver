"""Pydantic v2 request/response schemas for ScheduleSolver."""

from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

# --- Literal type aliases for constrained enum fields ---

RoleType = Literal["server", "cook", "cashier", "barista", "host", "manager", "general"]
ShiftStatus = Literal["scheduled", "open", "completed", "cancelled", "covered"]
ShiftType = Literal["morning", "afternoon", "evening"]
IncidentStatus = Literal["open", "in_progress", "resolved", "escalated"]
IncidentUrgency = Literal["critical", "high", "medium", "low"]
CallStatus = Literal["pending", "calling", "accepted", "declined", "no_answer"]


# --- Employee schemas ---

class EmployeeBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=5, max_length=255)
    phone: str = Field(min_length=1, max_length=30)
    role: RoleType
    skill_level: int = Field(default=1, ge=1, le=5)
    reliability_score: float = Field(default=0.7, ge=0.0, le=1.0)
    prefers_morning: bool = False
    prefers_evening: bool = False
    weekend_available: bool = False
    max_hours_weekly: int = Field(default=40, ge=1, le=168)
    is_active: bool = True
    hired_date: date


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeResponse(EmployeeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    hours_worked_this_week: float = 0.0


# --- Shift schemas ---

class ShiftBase(BaseModel):
    date: date
    start_time: str = Field(min_length=1, max_length=10)
    end_time: str = Field(min_length=1, max_length=10)
    shift_type: ShiftType
    role_required: RoleType
    min_skill_level: int = Field(default=1, ge=1, le=5)
    is_weekend: bool = False
    status: ShiftStatus = Field(default="scheduled")


class ShiftCreate(ShiftBase):
    assigned_employee_id: Optional[int] = None


class ShiftResponse(ShiftBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    assigned_employee_id: Optional[int] = None


# --- Incident schemas ---

class IncidentBase(BaseModel):
    incident_id: str = Field(min_length=1, max_length=20)
    shift_id: int
    original_employee_id: int
    reason: str = Field(min_length=1, max_length=500)
    urgency: IncidentUrgency
    status: IncidentStatus = Field(default="open")


class IncidentCreate(IncidentBase):
    pass


class IncidentResponse(IncidentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    replacement_employee_id: Optional[int] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None


# --- CallLog schemas ---

class CallLogBase(BaseModel):
    incident_id: int
    employee_id: int
    call_order: int
    status: CallStatus
    ml_score: float
    call_started_at: datetime
    call_ended_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    notes: Optional[str] = None


class CallLogResponse(CallLogBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


# --- Enriched response schemas (Phase 2) ---


class ShiftResponseEnriched(ShiftResponse):
    """Shift response with assigned employee name."""

    assigned_employee_name: Optional[str] = None


class IncidentCreateRequest(BaseModel):
    """Client-facing incident creation -- no incident_id (server-generated)."""

    shift_id: int
    original_employee_id: int
    reason: str = Field(min_length=1, max_length=500)
    urgency: IncidentUrgency


class IncidentResponseEnriched(IncidentResponse):
    """Incident response with inline employee/shift details."""

    original_employee_name: str = ""
    shift_date: Optional[date] = None
    shift_type: Optional[str] = None
    role_required: Optional[str] = None


# --- ML & Analytics schemas (contracts for Plan 02) ---


class CandidateRanking(BaseModel):
    """Single candidate in ML ranking results."""

    employee_id: int
    name: str
    role: str
    score: float
    reason: str
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "employee_id": 1,
                    "name": "Sarah Chen",
                    "role": "server",
                    "score": 0.87,
                    "reason": "Strong preference match, high reliability (0.92), exact role match",
                }
            ]
        }
    )


class RankRequest(BaseModel):
    shift_id: int


class RankResponse(BaseModel):
    shift_id: int
    role_required: str
    candidates: list[CandidateRanking]


class ModelInfoResponse(BaseModel):
    roc_auc: float
    accuracy: float
    precision: float
    recall: float
    feature_importances: dict[str, float]


class CoverageStatsResponse(BaseModel):
    avg_calls_to_resolution: float
    resolution_rate_percent: float
    avg_time_to_cover_seconds: float


class EmployeePerformanceResponse(BaseModel):
    employee_id: int
    name: str
    role: str
    total_calls: int
    accepted_calls: int
    acceptance_rate: float


# --- Agent schemas (Phase 6) ---


class AgentChatHistoryMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=5000)


class AgentChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    history: list[AgentChatHistoryMessage] = []


class AgentChatResponse(BaseModel):
    response: str
    tools_used: list[str] = []
    ollama_available: bool = True


class AgentStatusResponse(BaseModel):
    available: bool
    model: Optional[str] = None
    tools_count: int = 5
