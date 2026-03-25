[![CI](https://github.com/Piyush20001/ScheduleSolver/actions/workflows/ci.yml/badge.svg)](https://github.com/Piyush20001/ScheduleSolver/actions/workflows/ci.yml)
![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)
![TypeScript](https://img.shields.io/badge/TypeScript-5.6-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

# ScheduleSolver

ML-powered shift scheduling system for food service operations. When an employee calls out, XGBoost ranks replacement candidates across 7 features and the Command Center simulates the entire calling workflow in real time -- from ML ranking to call resolution -- in 15-30 seconds via WebSocket.

## Key Features

- **ML-Powered Candidate Ranking** -- XGBoost binary classifier (98%+ ROC-AUC) scores employees on reliability, skill match, preference alignment, and 4 more features
- **Real-Time Command Center** -- one-click demo triggers live calling simulation with animated progress, probability-weighted outcomes, and WebSocket event streaming
- **6 Interactive Pages** -- Dashboard, Employees, Schedule, Command Center, Analytics, AI Agent
- **Optional AI Agent** -- Ollama-powered chat with 5 tool-calling functions for natural language scheduling queries
- **Zero-Config First Run** -- `python run.py` trains the model, seeds the database, and starts the server automatically

## Table of Contents

- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
- [Architecture](#architecture)
- [How It Works](#how-it-works)
- [ML Model](#ml-model)
- [API Endpoints](#api-endpoints)
- [Environment Variables](#environment-variables)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Docker Deployment](#docker-deployment)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | React 18.3, TypeScript 5.6, Vite 6.0, Tailwind CSS v4, Recharts 2.14, TanStack Query 5.62, Framer Motion 11.12, Lucide Icons |
| **Backend** | Python 3.11, FastAPI 0.135, SQLAlchemy 2.0, SQLite, Pydantic v2, uvicorn |
| **ML Pipeline** | XGBoost 3.2, scikit-learn 1.8, pandas 3.0, numpy 2.4 |
| **AI Agent** | Ollama (optional), qwen2.5:7b / llama3.2 / mistral (auto-detected) |
| **DevOps** | GitHub Actions CI (lint + test + security scan), Docker Compose, ruff linter, nginx |

## Prerequisites

- **Python 3.11+** (for backend and ML pipeline)
- **Node.js 18+** and **npm** (for frontend)
- **Git** (to clone the repository)
- **Ollama** (optional, only for the AI Agent feature)

No database setup required -- SQLite is auto-created on first run.

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Piyush20001/ScheduleSolver.git
cd ScheduleSolver
```

### 2. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This installs FastAPI, XGBoost, scikit-learn, SQLAlchemy, and other dependencies.

### 3. Start the Backend

```bash
python run.py
```

**On first run**, this automatically:
1. Generates 25 synthetic employees with realistic food service profiles
2. Creates 12 weeks of shift history (~6,300 assignment records)
3. Trains an XGBoost model (takes ~5 seconds, achieves 98%+ ROC-AUC)
4. Saves the model to `app/ml/model.pkl` and metrics to `app/ml/metrics.json`
5. Seeds the database with demo employees, shifts, and incidents
6. Starts the API server at `http://localhost:8000`

**On subsequent runs**, the cached model and database load instantly.

You should see output like:
```
[INFO] Training XGBoost model...
[INFO] ROC-AUC: 0.984
[INFO] Model saved to app/ml/model.pkl
[INFO] Seeding database...
[INFO] Starting server at http://localhost:8000
```

### 4. Install Frontend Dependencies

Open a new terminal:

```bash
cd frontend
npm install
```

### 5. Start the Frontend

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

The Vite dev server proxies `/api` and `/ws` requests to the backend at `localhost:8000`, so everything works out of the box.

### 6. Explore the App

- **Dashboard** -- overview stats, activity feed, charts
- **Employees** -- searchable, filterable table of 25 employees
- **Schedule** -- weekly shift grid with open shift highlighting
- **Command Center** -- click "Trigger Demo" to watch the full ML ranking + calling simulation flow
- **Analytics** -- model performance metrics, feature importance, employee leaderboard
- **Agent** -- chat with the AI assistant (requires Ollama, see below)

### Optional: AI Agent Setup

The AI Agent page works without Ollama (shows a setup guide), but to enable chat:

```bash
# 1. Install Ollama from https://ollama.com

# 2. Pull a supported model (any of these work)
ollama pull qwen2.5:7b      # recommended (best tool calling)
ollama pull llama3.2         # lighter alternative
ollama pull mistral          # fallback option

# 3. Restart the backend -- it auto-detects Ollama on startup
cd backend && python run.py
```

The backend tries models in order: `qwen2.5:7b` → `llama3.2` → `mistral`, using the first one available.

## Architecture

```
┌─────────────────────┐              ┌──────────────────────────────────────┐
│    React Frontend    │    HTTP      │           FastAPI Backend            │
│    (Vite + TW v4)    │◄───────────►│                                      │
│                      │             │  ┌───────────┐   ┌───────────────┐   │
│  ┌────────────────┐  │   WebSocket │  │  XGBoost  │   │   SQLite DB   │   │
│  │  6 Pages       │  │◄───────────►│  │  Ranking  │   │  (zero cfg)   │   │
│  │  25 Components │  │             │  └───────────┘   └───────────────┘   │
│  │  TanStack Query│  │             │                                      │
│  │  Recharts      │  │             │  ┌───────────────────────────────┐   │
│  └────────────────┘  │             │  │  Ollama (optional)            │   │
│                      │             │  │  5 tool-calling functions     │   │
└─────────────────────┘              └──┴───────────────────────────────┴───┘
```

**Design decisions:**
- **XGBoost makes all ranking decisions** -- deterministic, explainable, no LLM in the ranking loop
- **Ollama is conversational only** -- natural language interface to the scheduling API via registered tools, never ranks directly
- **WebSocket pushes real-time updates** -- the Command Center shows live calling simulation with animated progress
- **Zero external dependencies** -- SQLite (no Postgres setup), file-based model (no MLflow), optional Ollama (graceful fallback)

### Request Flow

```
User clicks "Trigger Demo"
  → Frontend POST /api/incidents (creates incident)
  → Backend spawns async calling simulation
  → XGBoost ranks candidates (7 features → probability score)
  → For each candidate (top 5, sequentially):
      → WebSocket broadcasts "calling_candidate" event
      → Probability-weighted outcome (accept/decline/no_answer)
      → WebSocket broadcasts "call_result" event
  → If accepted → WebSocket broadcasts "incident_resolved"
  → Frontend updates UI in real-time via useWebSocket() hook
```

## How It Works

### ML Ranking Pipeline

1. **Data Generation** -- 25 hardcoded employees with realistic food service profiles (servers, cooks, cashiers, baristas, hosts, managers). 12 weeks of synthetic shift history with ~2% label noise.

2. **Feature Engineering** -- 7 features computed with point-in-time correctness (no future data leakage):

   | Feature | Range | What It Captures |
   |---------|-------|-----------------|
   | `reliability_score` | 0-1 | Historical shift acceptance rate |
   | `preference_match` | 0/1 | Morning/evening preference alignment |
   | `skill_gap` | -5 to +5 | Employee skill minus shift minimum |
   | `hours_remaining` | 0-40 | Weekly hours budget remaining |
   | `is_weekend_match` | 0/1 | Weekend availability alignment |
   | `role_match` | 0/0.4/1 | Exact (1.0), compatible (0.4), or incompatible (0) |
   | `days_since_last_shift` | 0-365 | Recency of last accepted shift |

3. **Training** -- XGBoost binary classifier with temporal split (weeks 1-10 train, 11-12 test). Achieves **0.984 ROC-AUC**.

4. **Inference** -- For each open shift, all compatible employees are scored. Top candidates get human-readable reason strings derived from their top 3 contributing features.

### Calling Simulation

When an incident is created, `calling_service.py` runs an async simulation:

1. Rank all compatible employees via XGBoost
2. Take top 5 candidates
3. Call each sequentially with probability-weighted outcomes:

   | ML Score | Accept | Decline | No Answer | Voicemail |
   |----------|--------|---------|-----------|-----------|
   | > 0.8 | 70% | 15% | 10% | 5% |
   | 0.5-0.8 | 40% | 25% | 20% | 15% |
   | < 0.5 | 15% | 30% | 30% | 25% |

4. Each call broadcasts WebSocket events for real-time UI updates
5. First acceptance resolves the incident; all exhausted triggers escalation

### AI Agent (Optional)

The agent registers 5 read-only tools in Ollama's function-calling format:

| Tool | What It Does |
|------|-------------|
| `rank_candidates` | ML-ranks employees for a specific shift |
| `find_open_shifts` | Queries shifts by date/role/status |
| `get_employee_info` | Fuzzy name search on employee records |
| `list_incidents` | Filters incidents by status |
| `get_coverage_stats` | Returns system-wide resolution metrics |

The LLM orchestrates tool calls to answer natural language questions (e.g., "Who should cover the next open shift?") but **never ranks candidates directly** -- that always goes through XGBoost.

## ML Model

| Property | Value |
|----------|-------|
| **Algorithm** | XGBoost binary classifier (`XGBClassifier`) |
| **ROC-AUC** | 0.984 (temporal split, weeks 11-12 held out) |
| **Accuracy** | 92% |
| **Precision** | 89% |
| **Recall** | 95% |
| **Features** | 7 (see feature table above) |
| **Top predictors** | `reliability_score` (32%), `preference_match` (28%) |
| **Training data** | ~6,300 (employee, shift) pairs across 12 weeks |
| **Label noise** | 2% injected for robustness |
| **Hyperparameters** | 200 estimators, max_depth=5, lr=0.05, subsample=0.8 |

**Why XGBoost?** Deterministic (same input = same output), explainable (feature importances drive human-readable reason strings), fast inference (~1ms per candidate), no GPU required.

## API Endpoints

### Employees
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/employees` | List employees. Filters: `role`, `weekend_available`, `min_reliability`, `skip`, `limit` |
| `POST` | `/api/employees` | Create employee (validated: role must be server/cook/cashier/barista/host/manager/general) |

### Shifts
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/shifts` | List shifts with assigned employee names. Filters: `start_date`, `end_date`, `skip`, `limit` |
| `POST` | `/api/shifts` | Create shift (validated: status must be scheduled/open/covered/cancelled) |

### Incidents
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/incidents` | List incidents with employee/shift details. Filters: `status`, `skip`, `limit` |
| `POST` | `/api/incidents` | Create incident -- **triggers async calling simulation** via WebSocket |

### ML & Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/recommendations/rank` | ML-rank candidates for a shift. Body: `{"shift_id": int}` |
| `GET` | `/api/analytics/model-info` | ROC-AUC, accuracy, precision, recall, feature importances |
| `GET` | `/api/analytics/coverage-stats` | Avg calls to resolution, resolution rate, avg time to cover |
| `GET` | `/api/analytics/employee-performance` | Per-employee acceptance rates, sorted descending |

### AI Agent
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/agent/status` | Ollama availability, detected model name, tool count |
| `POST` | `/api/agent/chat` | Chat with agent. Body: `{"message": str, "history": [...]}` |

### System
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check: `{"status": "healthy", "version": "2.0.0"}` |
| `WS` | `/ws` | WebSocket for real-time calling simulation events |

Interactive docs at [localhost:8000/docs](http://localhost:8000/docs) (Swagger) and [localhost:8000/redoc](http://localhost:8000/redoc).

## Environment Variables

### Backend

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CORS_ORIGINS` | No | `http://localhost:3000,http://localhost:5173` | Comma-separated allowed origins |
| `OLLAMA_URL` | No | `http://localhost:11434` | Ollama API endpoint |
| `OLLAMA_MODEL` | No | Auto-detected | Preferred Ollama model |

No database URL needed -- SQLite is created automatically at `backend/data/schedulesolver.db`.

### Frontend

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VITE_API_URL` | No | `http://localhost:8000` | Backend API base URL |

Copy `.env.example` files if you need to customize:

```bash
cp .env.example .env                    # backend
cp frontend/.env.example frontend/.env  # frontend
```

## Project Structure

```
ScheduleSolver/
├── backend/
│   ├── run.py                        # Entry point: train → seed → serve
│   ├── requirements.txt              # Python dependencies
│   ├── Dockerfile                    # Python 3.11-slim, non-root user
│   ├── app/
│   │   ├── main.py                   # FastAPI app, CORS, route registration
│   │   ├── database.py               # SQLAlchemy engine, session factory
│   │   ├── models.py                 # 4 tables: Employee, Shift, Incident, CallLog
│   │   ├── schemas.py                # Pydantic v2 models with Field validation
│   │   ├── websocket.py              # ConnectionManager singleton
│   │   ├── routers/
│   │   │   ├── employees.py          # CRUD with pagination + filters
│   │   │   ├── shifts.py             # CRUD with date range + pagination
│   │   │   ├── incidents.py          # CRUD + async calling simulation trigger
│   │   │   ├── recommendations.py    # POST /rank → ML candidate scoring
│   │   │   ├── analytics.py          # Model metrics, coverage stats, leaderboard
│   │   │   └── agent.py              # Ollama status check + chat endpoint
│   │   ├── services/
│   │   │   ├── ml_service.py         # Model loading, ranking, reason generation
│   │   │   ├── calling_service.py    # Async simulation with WebSocket events
│   │   │   ├── analytics_service.py  # Coverage and performance queries
│   │   │   └── agent_service.py      # Ollama integration, 5 tools, chat loop
│   │   └── ml/
│   │       ├── data_generator.py     # 25 employees, 12 weeks synthetic data
│   │       ├── feature_engineer.py   # 7 features, point-in-time correctness
│   │       └── train.py              # XGBoost training, temporal split
│   ├── scripts/
│   │   └── seed.py                   # Database seeder (idempotent)
│   └── tests/                        # 15 files, 123+ test functions
│       ├── conftest.py               # In-memory SQLite fixtures
│       ├── test_agent.py             # 32 tests: parsing, tools, endpoints
│       ├── test_api_*.py             # Endpoint tests for all 6 routers
│       ├── test_data_generator.py    # Data generation validation
│       ├── test_feature_engineer.py  # Feature computation correctness
│       ├── test_training.py          # Training pipeline, metrics
│       ├── test_websocket.py         # Connection, broadcast, cleanup
│       └── test_smoke.py             # Basic health checks
├── frontend/
│   ├── package.json                  # React 18, Vite 6, Tailwind v4
│   ├── vite.config.ts                # Dev server port 3000, API proxy
│   ├── tsconfig.json                 # Strict mode, path aliases
│   ├── Dockerfile                    # Multi-stage: Node 18 build → nginx
│   ├── nginx.conf                    # SPA routing, API proxy, WebSocket, caching
│   ├── index.html
│   └── src/
│       ├── main.tsx                  # React entry point
│       ├── App.tsx                   # Router with 6 pages
│       ├── pages/
│       │   ├── Dashboard.tsx         # Stat cards, activity feed, charts
│       │   ├── Employees.tsx         # Filterable, sortable employee table
│       │   ├── Schedule.tsx          # 7-day grid, week navigation
│       │   ├── CommandCenter.tsx     # 3-column: incidents, timeline, ranking
│       │   ├── Analytics.tsx         # ROC-AUC hero, feature importance
│       │   └── Agent.tsx             # 70/30 chat + context panel
│       ├── components/               # ~25 components organized by feature
│       │   ├── layout/              # Layout, Sidebar
│       │   ├── ui/                  # Button, Card, Badge, Skeleton, etc.
│       │   ├── dashboard/           # StatCards, ActivityFeed, charts
│       │   ├── employees/           # EmployeeTable, EmployeeFilters
│       │   ├── schedule/            # WeekGrid, ShiftCell, CandidatePanel
│       │   ├── command-center/      # ActiveIncidents, CallTimeline, etc.
│       │   ├── analytics/           # ModelMetricsHero, FeatureImportance
│       │   └── agent/               # ChatInterface, ToolCallCard, etc.
│       ├── hooks/
│       │   ├── api/                 # TanStack Query hooks per resource
│       │   ├── useWebSocket.ts      # WebSocket connection + reconnection
│       │   └── useDemoFlow.ts       # Demo orchestration state machine
│       ├── types/                   # TypeScript interfaces per domain
│       └── lib/
│           ├── api-client.ts        # Axios HTTP client
│           └── query-client.ts      # TanStack Query configuration
├── docker-compose.yml                # 2 services: backend + frontend
├── .github/workflows/ci.yml         # Lint + test + security scanning
├── ruff.toml                         # Python linter configuration
├── .env.example
├── CONTRIBUTING.md
└── LICENSE                           # MIT
```

## Testing

### Running Tests

```bash
cd backend

# Run all tests
python -m pytest tests/ -v

# Run a specific test file
python -m pytest tests/test_agent.py -v

# Run tests matching a pattern
python -m pytest tests/ -k "test_rank" -v
```

Tests use an in-memory SQLite database with pre-seeded fixtures -- no external services needed.

### Test Coverage

| Test File | Tests | What It Covers |
|-----------|-------|---------------|
| `test_agent.py` | 32 | Tool parsing, Ollama integration, regex fallback, chat loop, endpoints |
| `test_api_analytics.py` | 6 | Model info, coverage stats, employee performance |
| `test_api_employees.py` | 5 | List with filters, create with validation |
| `test_api_shifts.py` | 5 | List with date filters, create |
| `test_api_incidents.py` | 7 | List, create, async calling simulation |
| `test_api_recommendations.py` | 6 | ML ranking for various shifts |
| `test_data_generator.py` | 8 | Employee generation, shift history, noise injection |
| `test_feature_engineer.py` | 8 | Feature computation, point-in-time correctness |
| `test_training.py` | 10 | Training pipeline, metrics, temporal split |
| `test_websocket.py` | 7 | Connection, broadcast, disconnection |
| `test_seeder.py` | 5 | Database seeding, idempotency |
| `test_run.py` | 4 | Startup logic, model caching |
| `test_smoke.py` | 2 | API health check |

**Total: 123+ tests across 15 files**

### Linting

```bash
ruff check backend/    # Python linting (zero errors expected)
```

## Docker Deployment

### Quick Start with Docker Compose

```bash
docker compose up --build
```

This starts:
- **Backend** at [http://localhost:8000](http://localhost:8000) -- API + WebSocket
- **Frontend** at [http://localhost:3000](http://localhost:3000) -- nginx serving the React build

The backend auto-trains the model and seeds the database on first boot. A Docker volume (`backend-data`) persists the SQLite database and model artifacts across restarts.

### Production Architecture

```
                   ┌──────────────────────┐
  Browser ────────►│  nginx (port 80)     │
                   │  ├── /          → SPA │
                   │  ├── /api/*    → ──────────► backend:8000
                   │  └── /ws       → ──────────► backend:8000 (WebSocket)
                   └──────────────────────┘
```

Both containers run as non-root users (`appuser`) for security.

### Individual Container Builds

```bash
# Backend only
cd backend
docker build -t schedulesolver-backend .
docker run -p 8000:8000 -v backend-data:/app/data schedulesolver-backend

# Frontend only
cd frontend
docker build -t schedulesolver-frontend .
docker run -p 80:80 schedulesolver-frontend
```

## Troubleshooting

### Backend won't start

**Error:** `ModuleNotFoundError: No module named 'app'`

Run from the `backend/` directory:
```bash
cd backend
python run.py
```

### Model training fails

**Error:** `No module named 'xgboost'`

Install dependencies:
```bash
cd backend && pip install -r requirements.txt
```

### Frontend can't connect to backend

**Error:** Network errors or CORS issues

1. Verify backend is running at `http://localhost:8000`
2. Check that Vite proxy is configured (should work by default)
3. If running without Vite proxy, set `VITE_API_URL=http://localhost:8000` in `frontend/.env`

### WebSocket disconnects

The frontend auto-reconnects on WebSocket drops. If the "Connected" indicator in the sidebar footer shows disconnected:

1. Check that the backend is still running
2. Refresh the page

### AI Agent shows "Ollama not available"

This is expected if Ollama isn't installed. The rest of the app works without it. To enable:

```bash
# Install Ollama: https://ollama.com
ollama pull qwen2.5:7b
# Restart backend
```

### Docker Compose issues

**Error:** Port already in use

```bash
# Check what's using ports 8000 or 3000
lsof -i :8000
lsof -i :3000

# Or use different ports
docker compose up -p 8001:8000 -p 3001:80
```

**Error:** Backend exits immediately in Docker

The first run takes ~10 seconds to train the model. Check logs:
```bash
docker compose logs backend -f
```

## License

MIT -- see [LICENSE](LICENSE) for details.
