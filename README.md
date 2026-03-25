[![CI](https://github.com/Piyush20001/ScheduleSolver/actions/workflows/ci.yml/badge.svg)](https://github.com/Piyush20001/ScheduleSolver/actions/workflows/ci.yml)
![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

# ScheduleSolver

ML-powered shift scheduling system that uses XGBoost to rank replacement candidates when employees call out. The Command Center simulates the entire calling workflow in real time -- from ML ranking to call resolution -- in 15-30 seconds.

## Architecture

```
┌─────────────────┐         ┌─────────────────────────────────┐
│   React + TS    │  HTTP   │         FastAPI Backend          │
│   Vite + TW     │◄───────►│                                 │
│                 │         │  ┌─────────┐  ┌──────────────┐  │
│  Dashboard      │   WS    │  │ XGBoost │  │   SQLite DB  │  │
│  Employees      │◄───────►│  │ Ranking │  │  (zero cfg)  │  │
│  Schedule       │         │  └─────────┘  └──────────────┘  │
│  Command Center │         │                                 │
│  Analytics      │         │  ┌──────────────────────────┐   │
│  Agent (chat)   │         │  │  Ollama (optional)       │   │
│                 │         │  │  qwen2.5:7b tool calling │   │
└─────────────────┘         └──┴──────────────────────────┴───┘
```

**Key design decisions:**
- **XGBoost makes all ranking decisions** -- deterministic, explainable, no LLM in the loop
- **Ollama is conversational only** -- natural language interface to the scheduling API, never ranks directly
- **WebSocket pushes real-time updates** -- Command Center shows live calling simulation with animated progress

## Features

### Command Center
One-click incident resolution: ML-ranked candidates, animated calling simulation, and live WebSocket event stream. Click "Trigger Demo" to watch the full flow.

### ML-Powered Rankings
XGBoost scores every candidate across 7 features. Each ranking comes with score bars and human-readable explanations.

### Dashboard
Live stat cards, shift coverage charts, role distribution, and recent activity feed -- all backed by real data.

### Analytics
Model transparency dashboard: ROC-AUC score of 0.984, feature importance chart, resolution metrics, and employee reliability leaderboard.

### AI Agent (Optional)
Ollama-powered chat with tool calling. Ask natural language questions about employees, shifts, and rankings. Falls back to a clean setup guide when Ollama isn't installed.

### Schedule Management
Weekly grid with color-coded shifts, week navigation, and an ML candidate panel for open shifts.

## Quick Start

```bash
# Clone
git clone https://github.com/Piyush20001/ScheduleSolver.git
cd ScheduleSolver

# Backend
cd backend && pip install -r requirements.txt
python run.py  # trains model + seeds DB on first run

# Frontend (new terminal)
cd frontend && npm install
npm run dev
```

Open http://localhost:3000 -- backend API docs at http://localhost:8000/docs.

### Optional: AI Agent

```bash
# Install Ollama from https://ollama.com
ollama pull qwen2.5:7b
# Restart backend -- auto-detects Ollama on startup
```

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS v4, Recharts, TanStack Query |
| **Backend** | Python 3.11, FastAPI, SQLAlchemy, SQLite, Pydantic v2 |
| **ML** | XGBoost, scikit-learn, pandas, numpy |
| **AI** | Ollama (optional), qwen2.5:7b with function calling |
| **DevOps** | GitHub Actions CI, Docker Compose, ruff linter |

## How It Works

1. **First run** (`python run.py`): generates 25 synthetic employees, 12 weeks of shift history, trains XGBoost (98%+ ROC-AUC), seeds the database, starts the API server
2. **Subsequent runs**: loads cached model and database instantly
3. **Command Center**: creating an incident triggers background calling simulation -- XGBoost ranks candidates, simulates calls with probability-weighted outcomes, broadcasts every step over WebSocket
4. **AI Agent** (optional): registered tools (`rank_candidates`, `find_open_shifts`, `get_employee_info`) let the LLM answer scheduling questions without ever ranking directly

## ML Model

| Property | Value |
|----------|-------|
| **Algorithm** | XGBoost binary classifier |
| **ROC-AUC** | 98%+ (temporal split, weeks 11-12 held out) |
| **Features** | preference_match, skill_gap, reliability_score, hours_remaining, is_weekend_match, role_match, days_since_last_shift |
| **Top predictors** | reliability_score, preference_match |
| **Training data** | ~25 employees x 12 weeks, 2% label noise |

Why XGBoost? Deterministic (same input = same output), explainable (feature importances drive reason strings), fast inference, no GPU required.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/employees` | List employees (filterable, paginated) |
| `POST` | `/api/employees` | Create employee |
| `GET` | `/api/shifts` | List shifts (paginated) |
| `POST` | `/api/shifts` | Create shift |
| `GET` | `/api/incidents` | List incidents (paginated) |
| `POST` | `/api/incidents` | Create incident (triggers calling simulation) |
| `POST` | `/api/recommendations/rank` | ML-rank candidates for a shift |
| `GET` | `/api/analytics/model-info` | Model metrics and feature importances |
| `GET` | `/api/agent/status` | Ollama availability check |
| `POST` | `/api/agent/chat` | Chat with AI agent |
| `WS` | `/ws` | Real-time event stream |

Interactive docs at `/docs` (Swagger) and `/redoc`.

## Project Structure

```
ScheduleSolver/
├── backend/
│   ├── run.py                    # Entry point: train + seed + serve
│   ├── app/
│   │   ├── main.py               # FastAPI app, CORS, routes
│   │   ├── models.py             # Employee, Shift, Incident, CallLog
│   │   ├── schemas.py            # Pydantic models with validation
│   │   ├── routers/              # employees, shifts, incidents,
│   │   │                         #   recommendations, analytics, agent
│   │   ├── services/             # ml_service, calling_service,
│   │   │                         #   analytics_service, agent_service
│   │   ├── ml/                   # data_generator, feature_engineer, train
│   │   └── websocket.py          # ConnectionManager for broadcasts
│   ├── tests/                    # 120+ pytest tests
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── pages/                # Dashboard, Employees, Schedule,
│   │   │                         #   CommandCenter, Analytics, Agent
│   │   ├── components/           # UI primitives, page-specific components
│   │   ├── hooks/                # API hooks, useWebSocket, useDemoFlow
│   │   └── types/                # TypeScript interfaces
│   ├── Dockerfile                # Multi-stage nginx production build
│   └── nginx.conf                # SPA routing + API proxy
├── docker-compose.yml
├── .github/workflows/ci.yml     # Lint + test + security scanning
└── ruff.toml
```

## Docker

```bash
docker compose up --build
```

Backend at http://localhost:8000, frontend at http://localhost:3000.

## Tests

```bash
cd backend
python -m pytest tests/ -v     # 120+ tests
ruff check .                   # linting
```

## License

MIT -- see [LICENSE](LICENSE).
