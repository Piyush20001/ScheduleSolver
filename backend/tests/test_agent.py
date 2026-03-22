"""Tests for AI Agent service and router endpoints."""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch


from app.services.agent_service import ScheduleAgent


# ---------------------------------------------------------------------------
# Helper: build mock httpx response
# ---------------------------------------------------------------------------


def _mock_httpx_response(status_code=200, json_data=None):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data or {}
    resp.raise_for_status = MagicMock()
    return resp


# ---------------------------------------------------------------------------
# Fallback parser unit tests
# ---------------------------------------------------------------------------


class TestFallbackParser:
    """Test ScheduleAgent._parse_tool_calls with various inputs."""

    def setup_method(self):
        self.agent = ScheduleAgent()

    def test_standard_tool_calls(self):
        """Standard tool_calls array is parsed correctly."""
        message = {
            "tool_calls": [
                {"function": {"name": "find_open_shifts", "arguments": {"status": "open"}}}
            ]
        }
        result = self.agent._parse_tool_calls(message)
        assert len(result) == 1
        assert result[0]["name"] == "find_open_shifts"
        assert result[0]["arguments"] == {"status": "open"}

    def test_string_arguments(self):
        """String-encoded arguments are JSON-parsed."""
        message = {
            "tool_calls": [
                {"function": {"name": "rank_candidates", "arguments": '{"shift_id": 5}'}}
            ]
        }
        result = self.agent._parse_tool_calls(message)
        assert len(result) == 1
        assert result[0]["name"] == "rank_candidates"
        assert result[0]["arguments"] == {"shift_id": 5}

    def test_malformed_string_arguments(self):
        """Malformed string arguments default to empty dict."""
        message = {
            "tool_calls": [
                {"function": {"name": "get_employee_info", "arguments": "not valid json{"}}
            ]
        }
        result = self.agent._parse_tool_calls(message)
        assert len(result) == 1
        assert result[0]["name"] == "get_employee_info"
        assert result[0]["arguments"] == {}

    def test_no_tool_calls_plain_text(self):
        """Plain text response with no tool patterns returns empty list."""
        message = {"content": "Here are today's open shifts."}
        result = self.agent._parse_tool_calls(message)
        assert result == []

    def test_no_tool_calls_empty(self):
        """Empty message returns empty list."""
        result = self.agent._parse_tool_calls({})
        assert result == []

    def test_regex_fallback_tool_call_tags(self):
        """Regex fallback extracts from <tool_call> tags."""
        message = {
            "content": 'Let me check. <tool_call>{"name": "find_open_shifts", "arguments": {"status": "open"}}</tool_call>'
        }
        result = self.agent._parse_tool_calls(message)
        assert len(result) == 1
        assert result[0]["name"] == "find_open_shifts"

    def test_multiple_tool_calls(self):
        """Multiple tool calls in one response are all parsed."""
        message = {
            "tool_calls": [
                {"function": {"name": "find_open_shifts", "arguments": {}}},
                {"function": {"name": "get_coverage_stats", "arguments": {}}},
            ]
        }
        result = self.agent._parse_tool_calls(message)
        assert len(result) == 2
        assert result[0]["name"] == "find_open_shifts"
        assert result[1]["name"] == "get_coverage_stats"


# ---------------------------------------------------------------------------
# Tool execution tests (require seeded DB via client fixture)
# ---------------------------------------------------------------------------


class TestToolExecution:
    """Test individual tool execution with seeded test data."""

    def setup_method(self):
        self.agent = ScheduleAgent()

    def test_find_open_shifts(self, client, seed_shifts):
        result = json.loads(self.agent._execute_tool("find_open_shifts", {}))
        assert isinstance(result, list)
        # seed_shifts has 1 open shift (shift 2)
        assert len(result) >= 1
        assert any(s["status"] == "open" for s in result)

    def test_find_open_shifts_no_results(self, client, seed_shifts):
        result = json.loads(
            self.agent._execute_tool("find_open_shifts", {"status": "cancelled"})
        )
        assert result == []

    def test_get_employee_info(self, client, seed_employees):
        result = json.loads(
            self.agent._execute_tool("get_employee_info", {"employee_name": "Alice"})
        )
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["name"] == "Alice Manager"

    def test_get_employee_info_partial_match(self, client, seed_employees):
        result = json.loads(
            self.agent._execute_tool("get_employee_info", {"employee_name": "ar"})
        )
        # "Carol Server" matches "ar"
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_get_employee_info_no_name(self, client, seed_employees):
        result = json.loads(
            self.agent._execute_tool("get_employee_info", {})
        )
        assert "error" in result

    def test_list_incidents(self, client, seed_incidents):
        result = json.loads(self.agent._execute_tool("list_incidents", {}))
        assert isinstance(result, list)
        assert len(result) == 2  # 2 seeded incidents

    def test_list_incidents_filtered(self, client, seed_incidents):
        result = json.loads(
            self.agent._execute_tool("list_incidents", {"status": "open"})
        )
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["status"] == "open"

    def test_get_coverage_stats(self, client, seed_incidents):
        result = json.loads(self.agent._execute_tool("get_coverage_stats", {}))
        assert "avg_calls_to_resolution" in result
        assert "resolution_rate_percent" in result
        assert "avg_time_to_cover_seconds" in result

    def test_unknown_tool(self, client):
        result = json.loads(self.agent._execute_tool("nonexistent_tool", {}))
        assert "error" in result


# ---------------------------------------------------------------------------
# Agent status check tests (mock httpx)
# ---------------------------------------------------------------------------


def test_agent_available_with_model():
    agent = ScheduleAgent()
    mock_resp = _mock_httpx_response(200, {
        "models": [{"name": "qwen2.5:7b"}]
    })

    with patch("app.services.agent_service.httpx.AsyncClient") as MockClient:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = mock_client

        available, model = asyncio.run(agent.check_available())
        assert available is True
        assert model == "qwen2.5:7b"


def test_agent_unavailable_connection_error():
    agent = ScheduleAgent()

    with patch("app.services.agent_service.httpx.AsyncClient") as MockClient:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=Exception("Connection refused"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = mock_client

        available, model = asyncio.run(agent.check_available())
        assert available is False
        assert model is None


def test_agent_no_compatible_model():
    agent = ScheduleAgent()
    mock_resp = _mock_httpx_response(200, {
        "models": [{"name": "phi3:latest"}]
    })

    with patch("app.services.agent_service.httpx.AsyncClient") as MockClient:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = mock_client

        available, model = asyncio.run(agent.check_available())
        assert available is False
        assert model is None


def test_agent_model_fallback_chain():
    """When qwen2.5:7b is absent but llama3.2 is present, picks llama3.2."""
    agent = ScheduleAgent()
    mock_resp = _mock_httpx_response(200, {
        "models": [{"name": "llama3.2:latest"}]
    })

    with patch("app.services.agent_service.httpx.AsyncClient") as MockClient:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = mock_client

        available, model = asyncio.run(agent.check_available())
        assert available is True
        assert model == "llama3.2:latest"


# ---------------------------------------------------------------------------
# Agent chat tests (mock Ollama)
# ---------------------------------------------------------------------------


def test_chat_ollama_unavailable():
    agent = ScheduleAgent()

    with patch.object(agent, "check_available", new_callable=AsyncMock, return_value=(False, None)):
        result = asyncio.run(agent.chat("hello", []))
        assert result["ollama_available"] is False
        assert "unavailable" in result["response"].lower() or "not" in result["response"].lower()
        assert result["tools_used"] == []


def test_chat_plain_response():
    """Ollama returns plain text without tool calls."""
    agent = ScheduleAgent()
    ollama_response = {
        "message": {
            "role": "assistant",
            "content": "Hello! How can I help with scheduling?",
        },
        "done": True,
    }

    with patch.object(agent, "check_available", new_callable=AsyncMock, return_value=(True, "qwen2.5:7b")):
        mock_resp = _mock_httpx_response(200, ollama_response)

        with patch("app.services.agent_service.httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_resp)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_client

            result = asyncio.run(agent.chat("hello", []))
            assert result["ollama_available"] is True
            assert result["response"] == "Hello! How can I help with scheduling?"
            assert result["tools_used"] == []


def test_chat_with_tool_call():
    """Ollama requests a tool call, then gives final response."""
    agent = ScheduleAgent()

    # First response: tool call
    tool_call_response = {
        "message": {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {"function": {"name": "get_coverage_stats", "arguments": {}}}
            ],
        },
        "done": True,
    }
    # Second response: final text
    final_response = {
        "message": {
            "role": "assistant",
            "content": "The coverage rate is 50%.",
        },
        "done": True,
    }

    with patch.object(agent, "check_available", new_callable=AsyncMock, return_value=(True, "qwen2.5:7b")):
        mock_resp1 = _mock_httpx_response(200, tool_call_response)
        mock_resp2 = _mock_httpx_response(200, final_response)

        with patch("app.services.agent_service.httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(side_effect=[mock_resp1, mock_resp2])
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_client

            with patch.object(agent, "_execute_tool", return_value='{"avg_calls_to_resolution": 2.0}'):
                result = asyncio.run(agent.chat("How is our coverage?", []))
                assert result["ollama_available"] is True
                assert "50" in result["response"]
                assert "get_coverage_stats" in result["tools_used"]


def test_max_rounds_limit():
    """Chat loop stops after MAX_TOOL_ROUNDS even if Ollama keeps requesting tools."""
    agent = ScheduleAgent()

    # Always return a tool call
    tool_call_response = {
        "message": {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {"function": {"name": "find_open_shifts", "arguments": {}}}
            ],
        },
        "done": True,
    }

    with patch.object(agent, "check_available", new_callable=AsyncMock, return_value=(True, "qwen2.5:7b")):
        mock_resp = _mock_httpx_response(200, tool_call_response)

        with patch("app.services.agent_service.httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_resp)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_client

            with patch.object(agent, "_execute_tool", return_value="[]"):
                result = asyncio.run(agent.chat("Find all shifts", []))
                # Should have called post exactly MAX_TOOL_ROUNDS times (5)
                assert mock_client.post.call_count == 5
                assert "find_open_shifts" in result["tools_used"]


# ---------------------------------------------------------------------------
# HTTP endpoint tests via TestClient
# ---------------------------------------------------------------------------


def test_agent_status_endpoint(client):
    with patch(
        "app.routers.agent._agent.check_available",
        new_callable=AsyncMock,
        return_value=(True, "qwen2.5:7b"),
    ):
        resp = client.get("/api/agent/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["available"] is True
        assert data["model"] == "qwen2.5:7b"
        assert data["tools_count"] == 5


def test_agent_status_unavailable(client):
    with patch(
        "app.routers.agent._agent.check_available",
        new_callable=AsyncMock,
        return_value=(False, None),
    ):
        resp = client.get("/api/agent/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["available"] is False
        assert data["model"] is None


def test_agent_chat_endpoint(client):
    mock_result = {
        "response": "Hello!",
        "tools_used": [],
        "ollama_available": True,
    }
    with patch(
        "app.routers.agent._agent.chat",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        resp = client.post(
            "/api/agent/chat",
            json={"message": "hello"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["response"] == "Hello!"
        assert data["tools_used"] == []
        assert data["ollama_available"] is True


def test_agent_chat_with_history(client):
    mock_result = {
        "response": "Here are the open shifts.",
        "tools_used": ["find_open_shifts"],
        "ollama_available": True,
    }
    with patch(
        "app.routers.agent._agent.chat",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        resp = client.post(
            "/api/agent/chat",
            json={
                "message": "Show me shifts",
                "history": [
                    {"role": "user", "content": "hello"},
                    {"role": "assistant", "content": "Hi!"},
                ],
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["tools_used"] == ["find_open_shifts"]


def test_agent_router_registered():
    from app.main import app

    paths = [r.path for r in app.routes if hasattr(r, "path")]
    assert "/api/agent/status" in paths
    assert "/api/agent/chat" in paths


# ---------------------------------------------------------------------------
# Agent service contract checks
# ---------------------------------------------------------------------------


def test_agent_has_5_tools():
    """Agent registers exactly 5 tools."""
    agent = ScheduleAgent()
    assert len(agent.tools) == 5


def test_agent_tool_names():
    """Agent tools have the expected names."""
    agent = ScheduleAgent()
    names = {t["function"]["name"] for t in agent.tools}
    expected = {"find_open_shifts", "rank_candidates", "get_employee_info", "list_incidents", "get_coverage_stats"}
    assert names == expected


def test_agent_session_isolation():
    """Agent service uses SessionLocal() directly (same pattern as calling_service)."""
    import inspect
    import app.services.agent_service as agent_mod

    source = inspect.getsource(agent_mod)
    assert "SessionLocal()" in source, "agent_service must use SessionLocal()"
    assert "Depends(get_db)" not in source, "agent_service must not use Depends(get_db)"
