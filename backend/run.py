#!/usr/bin/env python3
"""ScheduleSolver v2 -- Entry point.

First run: trains XGBoost model, seeds database, starts server.
Subsequent runs: loads cached artifacts, boots instantly.
"""

import json
import os
import sys

# Fix sys.path so app.* imports work regardless of CWD
_backend_dir = os.path.dirname(os.path.abspath(__file__))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)


def main():
    """Entry point for ScheduleSolver."""
    no_serve = "--no-serve" in sys.argv

    model_path = os.path.join(_backend_dir, "app", "ml", "model.pkl")
    metrics_path = os.path.join(_backend_dir, "app", "ml", "metrics.json")

    if not os.path.exists(model_path):
        # First run: train model + seed database
        print("[INFO] First run detected")

        from app.ml.train import train_model
        train_model()

        from app.database import SessionLocal, init_db
        init_db()

        session = SessionLocal()
        try:
            from scripts.seed import seed_database
            seed_database(session)
        finally:
            session.close()
    else:
        # Subsequent run: load cached artifacts
        with open(metrics_path) as f:
            metrics = json.load(f)
        print(f"[OK]   Model loaded (ROC-AUC: {metrics['roc_auc']})")

        from app.database import SessionLocal
        session = SessionLocal()
        try:
            from app.models import Employee
            emp_count = session.query(Employee).count()
            print(f"[OK]   Database ready ({emp_count} employees)")
        finally:
            session.close()

    # Ollama detection
    try:
        import httpx
        resp = httpx.get("http://localhost:11434/api/tags", timeout=2.0)
        if resp.status_code == 200:
            models = [m["name"] for m in resp.json().get("models", [])]
            preferred = ["qwen2.5:7b", "qwen2.5:latest", "llama3.2:latest", "llama3.2", "mistral:latest", "mistral"]
            detected = next((m for m in preferred if any(m in name for name in models)), None)
            if detected:
                print(f"[OK]   Ollama detected ({detected}) -- AI Agent enabled")
            elif models:
                print(f"[WARN] Ollama running but no supported model found. Available: {', '.join(models)}")
                print("       Run: ollama pull qwen2.5:7b")
            else:
                print("[WARN] Ollama running but no models loaded. Run: ollama pull qwen2.5:7b")
        else:
            print("[INFO] Ollama not detected -- AI Agent disabled. To enable: ollama pull qwen2.5:7b && ollama serve")
    except Exception:
        print("[INFO] Ollama not detected -- AI Agent disabled. To enable: ollama pull qwen2.5:7b && ollama serve")

    # Start server
    if not no_serve:
        import uvicorn
        print("[INFO] Starting server at http://localhost:8000")
        uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    main()
