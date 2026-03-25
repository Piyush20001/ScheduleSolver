"""AI Agent service: Ollama-powered chat with tool calling.

Registers 5 read-only tools that map to internal DB queries and existing
services.  The LLM orchestrates conversation; XGBoost always ranks.
"""

import json
import logging
import re
from datetime import date, timedelta

import httpx

from app.database import SessionLocal
from app.ml.data_generator import COMPATIBLE_ROLES
from app.models import Employee, Incident, Shift
from app.services import analytics_service, ml_service

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tool definitions (Ollama / OpenAI function-calling format)
# ---------------------------------------------------------------------------

AGENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "find_open_shifts",
            "description": "Find shifts that need coverage. Can filter by date, role, or status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "Filter by date: YYYY-MM-DD, 'today', or 'tomorrow'. Optional.",
                    },
                    "role": {
                        "type": "string",
                        "description": "Filter by required role (e.g. server, cook). Optional.",
                    },
                    "status": {
                        "type": "string",
                        "description": "Shift status filter. Defaults to 'open'. Options: open, scheduled, covered, cancelled.",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "rank_candidates",
            "description": "Get ML-ranked employee recommendations for a specific shift using the XGBoost model. Returns employees sorted by suitability score.",
            "parameters": {
                "type": "object",
                "properties": {
                    "shift_id": {
                        "type": "integer",
                        "description": "The ID of the shift to rank candidates for.",
                    },
                },
                "required": ["shift_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_employee_info",
            "description": "Get details about a specific employee by name search. Returns matching employees with their skills, reliability, and preferences.",
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_name": {
                        "type": "string",
                        "description": "Full or partial employee name to search for.",
                    },
                },
                "required": ["employee_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_incidents",
            "description": "List scheduling incidents. Can filter by status (open, in_progress, resolved, escalated).",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "Filter by incident status: open, in_progress, resolved, escalated. Optional -- returns all if omitted.",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_coverage_stats",
            "description": "Get system-wide coverage statistics: average calls to resolution, resolution rate, and average time to cover.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = (
    "You are ScheduleSolver AI, an intelligent scheduling assistant for restaurant managers. "
    "You help find shift coverage, rank employee candidates, and manage scheduling emergencies.\n\n"
    "IMPORTANT RULES:\n"
    "- ALWAYS use tools to answer questions about employees, shifts, incidents, and statistics.\n"
    "- NEVER guess or make up employee data, rankings, or statistics.\n"
    "- When asked about who should cover a shift, ALWAYS use the rank_candidates tool.\n"
    "- Be concise and operational. Managers are busy.\n"
    "- Format responses with clear structure when presenting data."
)

# ---------------------------------------------------------------------------
# Model preference list (D-12)
# ---------------------------------------------------------------------------

PREFERRED_MODELS = [
    "qwen2.5:7b",
    "qwen2.5:latest",
    "llama3.2:latest",
    "llama3.2",
    "mistral:latest",
    "mistral",
]

# ---------------------------------------------------------------------------
# ScheduleAgent class
# ---------------------------------------------------------------------------

MAX_TOOL_ROUNDS = 5


class ScheduleAgent:
    """Ollama-powered scheduling agent with tool calling."""

    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.tools = AGENT_TOOLS
        self.ollama_timeout = 30.0
        self.status_timeout = 2.0

    # -- Availability check ---------------------------------------------------

    async def check_available(self) -> tuple[bool, str | None]:
        """Check if Ollama is running and find a compatible model.

        Returns:
            (True, model_name) when a supported model is found.
            (False, None) otherwise.
        """
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{self.ollama_url}/api/tags",
                    timeout=self.status_timeout,
                )
            if resp.status_code != 200:
                return False, None

            model_names = [m.get("name", "") for m in resp.json().get("models", [])]
            for preferred in PREFERRED_MODELS:
                for available in model_names:
                    if preferred in available:
                        return True, preferred
            return False, None
        except Exception:
            return False, None

    # -- Chat loop -------------------------------------------------------------

    async def chat(self, message: str, history: list[dict]) -> dict:
        """Run a chat turn with optional tool calling (max 5 rounds).

        Args:
            message: The user's latest message.
            history: Prior conversation messages [{role, content}, ...].

        Returns:
            Dict with keys: response, tools_used, ollama_available.
        """
        available, model = await self.check_available()
        if not available:
            return {
                "response": (
                    "AI Agent is currently unavailable. Ollama is not running "
                    "locally. To enable: install Ollama from ollama.com, pull a "
                    "model with 'ollama pull qwen2.5:7b', then start with "
                    "'ollama serve'."
                ),
                "tools_used": [],
                "ollama_available": False,
            }

        # Build messages array
        messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]
        for h in history:
            # Sanitize history: strip tool_call tags that could trigger tool execution
            sanitized_content = re.sub(r'</?tool_call>', '', h["content"]).strip()
            messages.append({"role": h["role"], "content": sanitized_content})
        # Sanitize user input: strip tool_call tags that could trigger tool execution
        sanitized_message = re.sub(r'</?tool_call>', '', message).strip()
        messages.append({"role": "user", "content": sanitized_message})

        tools_used: set[str] = set()
        final_content = ""

        try:
            async with httpx.AsyncClient() as client:
                for _round in range(MAX_TOOL_ROUNDS):
                    resp = await client.post(
                        f"{self.ollama_url}/api/chat",
                        json={
                            "model": model,
                            "messages": messages,
                            "tools": self.tools,
                            "stream": False,
                        },
                        timeout=self.ollama_timeout,
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    response_message = data.get("message", {})

                    # Parse for tool calls
                    tool_calls = self._parse_tool_calls(response_message)

                    if not tool_calls:
                        # Final text response -- exit loop
                        final_content = response_message.get("content", "")
                        break

                    # Execute tool calls
                    # Append assistant message (preserve tool_calls)
                    messages.append(response_message)

                    for tc in tool_calls:
                        tool_name = tc["name"]
                        tool_args = tc["arguments"]
                        tools_used.add(tool_name)

                        result = self._execute_tool(tool_name, tool_args)
                        messages.append({"role": "tool", "content": result})
                else:
                    # Exhausted MAX_TOOL_ROUNDS
                    final_content = response_message.get("content", "")
                    if not final_content:
                        final_content = (
                            "I've used all available tool calls for this request. "
                            "Here's what I found so far based on the tool results above."
                        )

        except Exception as exc:
            logger.exception("Agent chat error")
            return {
                "response": f"I encountered an error while processing your request: {exc}",
                "tools_used": list(tools_used),
                "ollama_available": True,
            }

        return {
            "response": final_content,
            "tools_used": list(tools_used),
            "ollama_available": True,
        }

    # -- Fallback parser -------------------------------------------------------

    def _parse_tool_calls(self, message: dict) -> list[dict]:
        """Extract tool calls from an Ollama response message.

        Tries three strategies in order:
        1. Standard ``tool_calls`` array (happy path).
        2. String-encoded arguments inside ``tool_calls``.
        3. Regex fallback on ``content`` for ``<tool_call>`` blocks.
        """
        # Strategy 1 & 2: standard tool_calls
        raw_calls = message.get("tool_calls")
        if raw_calls:
            parsed: list[dict] = []
            for tc in raw_calls:
                func = tc.get("function", {})
                name = func.get("name", "")
                args = func.get("arguments", {})
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except (json.JSONDecodeError, TypeError):
                        args = {}
                if name:
                    parsed.append({"name": name, "arguments": args})
            return parsed

        # Strategy 3: regex fallback on content
        content = message.get("content", "")
        if not content:
            return []

        # Pattern: <tool_call>{"name": "...", "arguments": {...}}</tool_call>
        pattern = r"<tool_call>\s*(\{.*?\})\s*</tool_call>"
        matches = re.findall(pattern, content, re.DOTALL)
        if matches:
            parsed = []
            for match in matches:
                try:
                    obj = json.loads(match)
                    name = obj.get("name", "")
                    args = obj.get("arguments", {})
                    if name:
                        parsed.append({"name": name, "arguments": args})
                except json.JSONDecodeError:
                    pass
            if parsed:
                return parsed

        # Pattern: {"name": "tool_name", "arguments": {...}} outside tags
        pattern2 = r'\{\s*"name"\s*:\s*"(\w+)"\s*,\s*"arguments"\s*:\s*(\{[^}]*\})\s*\}'
        matches2 = re.findall(pattern2, content, re.DOTALL)
        if matches2:
            parsed = []
            for name, args_str in matches2:
                try:
                    args = json.loads(args_str)
                except json.JSONDecodeError:
                    args = {}
                parsed.append({"name": name, "arguments": args})
            if parsed:
                return parsed

        return []

    # -- Tool execution --------------------------------------------------------

    def _execute_tool(self, name: str, arguments: dict) -> str:
        """Execute a registered tool and return JSON string result."""
        session = SessionLocal()
        try:
            if name == "find_open_shifts":
                return self._tool_find_open_shifts(session, arguments)
            elif name == "rank_candidates":
                return self._tool_rank_candidates(session, arguments)
            elif name == "get_employee_info":
                return self._tool_get_employee_info(session, arguments)
            elif name == "list_incidents":
                return self._tool_list_incidents(session, arguments)
            elif name == "get_coverage_stats":
                return self._tool_get_coverage_stats(session, arguments)
            else:
                return json.dumps({"error": f"Unknown tool: {name}"})
        except Exception as exc:
            logger.exception(f"Tool execution failed: {name}")
            return json.dumps({"error": f"Tool execution failed: {str(exc)}"})
        finally:
            session.close()

    # -- Individual tool implementations ---------------------------------------

    def _tool_find_open_shifts(self, session, arguments: dict) -> str:
        query = session.query(Shift)

        status_filter = arguments.get("status", "open")
        query = query.filter(Shift.status == status_filter)

        date_arg = arguments.get("date")
        if date_arg:
            if date_arg == "today":
                target_date = date.today()
            elif date_arg == "tomorrow":
                target_date = date.today() + timedelta(days=1)
            else:
                try:
                    target_date = date.fromisoformat(date_arg)
                except ValueError:
                    target_date = None
            if target_date:
                query = query.filter(Shift.date == target_date)

        role_arg = arguments.get("role")
        if role_arg:
            query = query.filter(Shift.role_required == role_arg)

        shifts = query.all()
        results = []
        for s in shifts:
            emp_name = None
            if s.assigned_employee_id:
                emp = session.query(Employee).filter(Employee.id == s.assigned_employee_id).first()
                emp_name = emp.name if emp else None
            results.append({
                "id": s.id,
                "date": s.date.isoformat(),
                "start_time": s.start_time,
                "end_time": s.end_time,
                "shift_type": s.shift_type,
                "role_required": s.role_required,
                "status": s.status,
                "assigned_employee": emp_name,
            })
        return json.dumps(results)

    def _tool_rank_candidates(self, session, arguments: dict) -> str:
        shift_id = arguments.get("shift_id")
        if shift_id is None:
            return json.dumps({"error": "shift_id is required"})

        shift = session.query(Shift).filter(Shift.id == int(shift_id)).first()
        if not shift:
            return json.dumps({"error": f"Shift {shift_id} not found"})

        compatible_roles = COMPATIBLE_ROLES.get(shift.role_required, {shift.role_required})
        employees = (
            session.query(Employee)
            .filter(
                Employee.is_active == True,  # noqa: E712
                Employee.role.in_(compatible_roles),
            )
            .all()
        )

        if not employees:
            return json.dumps({"error": "No compatible employees found", "shift_id": shift_id})

        ranked = ml_service.rank_candidates(shift, employees)
        return json.dumps(ranked)

    def _tool_get_employee_info(self, session, arguments: dict) -> str:
        name = arguments.get("employee_name", "")
        if not name:
            return json.dumps({"error": "employee_name is required"})

        employees = (
            session.query(Employee)
            .filter(Employee.name.ilike(f"%{name}%"))
            .all()
        )
        results = []
        for e in employees:
            results.append({
                "id": e.id,
                "name": e.name,
                "role": e.role,
                "skill_level": e.skill_level,
                "reliability_score": e.reliability_score,
                "prefers_morning": e.prefers_morning,
                "prefers_evening": e.prefers_evening,
                "weekend_available": e.weekend_available,
                "hours_worked_this_week": e.hours_worked_this_week,
                "max_hours_weekly": e.max_hours_weekly,
                "is_active": e.is_active,
            })
        return json.dumps(results)

    def _tool_list_incidents(self, session, arguments: dict) -> str:
        query = session.query(Incident)
        status_filter = arguments.get("status")
        if status_filter:
            query = query.filter(Incident.status == status_filter)

        incidents = query.all()
        results = []
        for inc in incidents:
            orig_emp = session.query(Employee).filter(Employee.id == inc.original_employee_id).first()
            shift = session.query(Shift).filter(Shift.id == inc.shift_id).first()
            results.append({
                "id": inc.id,
                "incident_id": inc.incident_id,
                "status": inc.status,
                "reason": inc.reason,
                "urgency": inc.urgency,
                "original_employee": orig_emp.name if orig_emp else None,
                "shift_date": shift.date.isoformat() if shift else None,
                "shift_type": shift.shift_type if shift else None,
                "role_required": shift.role_required if shift else None,
                "created_at": inc.created_at.isoformat() if inc.created_at else None,
                "resolved_at": inc.resolved_at.isoformat() if inc.resolved_at else None,
            })
        return json.dumps(results)

    def _tool_get_coverage_stats(self, session, arguments: dict) -> str:
        stats = analytics_service.get_coverage_stats(session)
        return json.dumps(stats)
