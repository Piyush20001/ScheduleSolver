[![CI](https://github.com/yourusername/schedulesolver/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/schedulesolver/actions/workflows/ci.yml)
![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

# ScheduleSolver

ML-powered shift scheduling system that uses XGBoost to rank replacement candidates when employees call out, with a real-time Command Center that simulates the entire calling workflow in 15-30 seconds.

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

- **XGBoost makes all ranking decisions** -- deterministic, explainable, no LLM involved
- **Ollama is conversational only** -- natural language interface to the scheduling API, never ranks directly
- **WebSocket enables real-time updates** -- Command Center shows live calling simulation with animated progress

## Features

### Command Center
Real-time incident resolution with ML-ranked candidates, animated calling simulation, and live WebSocket updates. Click "Trigger Demo" to see the full flow.

![Command Center](https://via.placeholder.com/800x450?text=Command+Center+Screenshot)

### ML-Powered Rankings
XGBoost scores every candidate with 7 features, showing score bars and human-readable explanations for each ranking decision.

![ML Rankings](https://via.placeholder.com/800x450?text=ML+Rankings+Screenshot)

### Dashboard
Live stat cards, shift coverage charts, role distribution, and recent activity feed -- all populated from real backend data.

![Dashboard](https://via.placeholder.com/800x450?text=Dashboard+Screenshot)

### Analytics
Model transparency: ROC-AUC metric, feature importance bar chart, resolution metrics, and employee reliability leaderboard.

![Analytics](https://via.placeholder.com/800x450?text=Analytics+Screenshot)

### AI Agent (Optional)
Ollama-powered chat with tool calling -- ask natural language questions about employees, shifts, and rankings. Clean fallback UI when Ollama isn't installed.

![AI Agent](https://via.placeholder.com/800x450?text=AI+Agent+Screenshot)

### Schedule Management
Weekly grid view with color-coded shifts (blue/yellow/green/grey), week navigation, and ML candidate panel for open shifts.

![Schedule](https://via.placeholder.com/800x450?text=Schedule+Screenshot)

## Quick Start

```bash
# 1. Clone
git clone https://github.com/yourusername/schedulesolver.git
cd schedulesolver

# 2. Install backend
cd backend && pip install -r requirements.txt

# 3. Start backend (trains model + seeds DB on first run)
python run.py

# 4. Install frontend (new terminal)
cd frontend && npm install

# 5. Start frontend
npm run dev
```

Open http://localhost:5173 -- backend runs at http://localhost:8000/docs (Swagger UI).

### Optional: AI Agent Setup

```bash
# 1. Install Ollama from https://ollama.com
# 2. Pull the model
ollama pull qwen2.5:7b
# 3. Restart backend -- it auto-detects Ollama on startup
```

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS v4, Recharts, TanStack Query |
| **Backend** | Python 3.11, FastAPI, SQLAlchemy, SQLite, Pydantic |
| **ML** | XGBoost, scikit-learn, pandas, numpy |
| **AI** | Ollama (optional), qwen2.5:7b with tool calling |
| **DevOps** | GitHub Actions CI, Docker Compose, ruff linter |

## How It Works

1. **First run** (`python run.py`): generates 25 synthetic employees, 12 weeks of shift history, trains an XGBoost model (98%+ ROC-AUC), seeds the database with demo data, and starts the server
2. **Subsequent runs**: loads cached model and database instantly
3. **Command Center demo**: creating an incident triggers background calling simulation -- XGBoost ranks candidates, simulates calls with probability-weighted outcomes, broadcasts every step via WebSocket
4. **AI Agent** (optional): Ollama chat uses registered tools (`rank_candidates`, `find_open_shifts`, `get_employee_info`) to answer scheduling questions -- never ranks directly

## ML Model

- **Algorithm:** XGBoost binary classifier
- **ROC-AUC:** 98%+ on temporal test split (weeks 11-12 held out)
- **Features (7):** preference_match, skill_gap, reliability_score, hours_remaining, is_weekend_match, role_match, days_since_last_shift
- **Top features:** reliability_score and preference_match dominate importance
- **Training data:** ~25 employees x 12 weeks of synthetic shift assignments with 2% label noise

Why XGBoost? Deterministic (same input = same output), explainable (feature importances drive reason strings), fast inference, no GPU needed.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/api/employees` | List employees (filterable by role, availability) |
| `POST` | `/api/employees` | Create employee |
| `GET` | `/api/shifts` | List shifts |
| `POST` | `/api/shifts` | Create shift |
| `GET` | `/api/incidents` | List incidents |
| `POST` | `/api/incidents` | Create incident (triggers calling simulation) |
| `POST` | `/api/recommendations/rank` | ML-rank candidates for a shift |
| `GET` | `/api/analytics/model-info` | Model metrics and feature importances |
| `GET` | `/api/agent/status` | Check Ollama availability |
| `POST` | `/api/agent/chat` | Chat with AI agent |
| `WS` | `/ws` | WebSocket for real-time events |

Full interactive docs at `/docs` (Swagger UI) and `/redoc`.

## Project Structure

```
schedulesolver/
├── backend/
│   ├── run.py                    # Entry point (train + seed + serve)
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── app/
│   │   ├── main.py               # FastAPI app with CORS + routes
│   │   ├── database.py           # SQLAlchemy engine + session
│   │   ├── models.py             # Employee, Shift, Incident, CallLog
│   │   ├── schemas.py            # Pydantic request/response models
│   │   ├── routers/              # employees, shifts, incidents,
│   │   │                         #   recommendations, analytics, agent
│   │   ├── services/             # ml_service, analytics_service,
│   │   │                         #   calling_service, agent_service
│   │   ├── ml/                   # data_generator, feature_engineer,
│   │   │                         #   train (+ model.pkl, metrics.json)
│   │   └── websocket.py          # ConnectionManager for broadcasts
│   ├── scripts/seed.py           # Database seeder
│   └── tests/                    # pytest suite (120+ tests)
├── frontend/
│   ├── package.json
│   ├── Dockerfile
│   ├── vite.config.ts
│   ├── index.html
│   └── src/
│       ├── pages/                # Dashboard, Employees, Schedule,
│       │                         #   CommandCenter, Analytics, Agent
│       ├── components/           # Sidebar, ScoreBar, UI primitives
│       ├── hooks/                # useApi, useWebSocket, useDemoFlow
│       ├── types/                # TypeScript interfaces
│       └── lib/                  # API client, utilities
├── docker-compose.yml            # Backend + frontend services
├── .github/workflows/ci.yml     # Lint + test CI
├── ruff.toml                     # Python linter config
├── LICENSE                       # MIT
└── CONTRIBUTING.md               # Contributor guide
```

## Docker

```bash
docker compose up --build
```

Backend at http://localhost:8000, frontend at http://localhost:5173.

## Running Tests

```bash
cd backend
python -m pytest tests/ -v
```

Linting:

```bash
ruff check backend/
```

## License

MIT License -- see [LICENSE](LICENSE) for details.
