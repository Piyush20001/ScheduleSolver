"""AI Agent router: Ollama-powered chat with tool calling."""

from fastapi import APIRouter

from app.schemas import AgentChatRequest, AgentChatResponse, AgentStatusResponse
from app.services.agent_service import ScheduleAgent

router = APIRouter(prefix="/api/agent", tags=["Agent"])

# Singleton agent instance
_agent = ScheduleAgent()


@router.get("/status", response_model=AgentStatusResponse)
async def agent_status():
    """Check if Ollama is available and which model is loaded."""
    available, model = await _agent.check_available()
    return AgentStatusResponse(
        available=available,
        model=model,
        tools_count=len(_agent.tools),
    )


@router.post("/chat", response_model=AgentChatResponse)
async def agent_chat(request: AgentChatRequest):
    """Send a message to the AI agent. Returns response with tool call metadata."""
    history = [{"role": m.role, "content": m.content} for m in request.history]
    result = await _agent.chat(request.message, history)
    return AgentChatResponse(**result)
