"""FastAPI application for ScheduleSolver v2."""

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocketDisconnect

from app.routers import agent, analytics, employees, incidents, recommendations, shifts
from app.websocket import manager

app = FastAPI(title="ScheduleSolver", version="2.0.0", docs_url="/docs", redoc_url="/redoc")

# CORS -- allow all origins in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register CRUD routers
app.include_router(employees.router)
app.include_router(shifts.router)
app.include_router(incidents.router)

# Register ML & Analytics routers
app.include_router(recommendations.router)
app.include_router(analytics.router)

# Register Agent router (Ollama AI)
app.include_router(agent.router)


@app.get("/")
def health_check():
    return {"status": "healthy", "version": "2.0.0"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time event broadcasting."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive -- listen for client messages (ping/pong)
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
