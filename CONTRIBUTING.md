# Contributing to ScheduleSolver

Thanks for your interest in contributing! This guide covers the basics.

## Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **Git**

## Development Setup

```bash
# Clone
git clone https://github.com/yourusername/schedulesolver.git
cd schedulesolver

# Backend
cd backend
pip install -r requirements.txt
python run.py  # trains model + seeds DB on first run

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

## Running Tests

```bash
cd backend
python -m pytest tests/ -v
```

All tests use in-memory SQLite -- no external services needed.

## Linting

```bash
ruff check backend/
```

Fix auto-fixable issues:

```bash
ruff check backend/ --fix
```

Configuration is in `ruff.toml` at the project root.

## Pull Request Guidelines

1. **Fork** the repository and create a feature branch
2. **Write tests** for new functionality
3. **Run lint** (`ruff check backend/`) -- must pass with zero errors
4. **Run tests** (`cd backend && pytest tests/ -v`) -- all must pass
5. **Keep commits focused** -- one logical change per commit
6. **Submit a PR** with a clear description of what changed and why

## Code Style

- Follow existing patterns in the codebase
- Short comments only where logic is non-obvious
- Practical variable names (`avail_hours`, not `employeeAvailabilityHoursRemaining`)
- Python: enforced by ruff (E, F, W rules, 120 char line length)
- TypeScript: follow existing component patterns

## Project Structure

- `backend/app/` -- FastAPI application code
- `backend/app/ml/` -- ML pipeline (data generation, feature engineering, training)
- `backend/app/routers/` -- API route handlers
- `backend/app/services/` -- Business logic layer
- `backend/tests/` -- pytest test suite
- `frontend/src/` -- React application

## Questions?

Open an issue and we'll help out.
