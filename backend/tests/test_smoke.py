"""Integration smoke tests for ScheduleSolver v2.

These tests verify the full system boots and responds correctly.
They complement per-phase unit tests by testing end-to-end behavior.
"""

import json
import os


# ---------------------------------------------------------------------------
# ML Pipeline Smoke Tests
# ---------------------------------------------------------------------------

class TestMLSmoke:
    """Verify the ML pipeline produces a valid model."""

    def test_model_trains_and_achieves_target_auc(self, tmp_model_dir):
        """Train model on synthetic data, verify ROC-AUC >= 0.98."""
        from app.ml.train import train_model

        train_model(output_dir=tmp_model_dir)

        model_path = os.path.join(tmp_model_dir, "model.pkl")
        metrics_path = os.path.join(tmp_model_dir, "metrics.json")

        assert os.path.exists(model_path), "model.pkl should be created"
        assert os.path.exists(metrics_path), "metrics.json should be created"

        with open(metrics_path) as f:
            metrics = json.load(f)

        assert metrics["roc_auc"] >= 0.98, f"ROC-AUC {metrics['roc_auc']} should be >= 0.98"
        assert "accuracy" in metrics
        assert "feature_importances" in metrics

    def test_feature_engineering_produces_seven_features(self):
        """Feature engineering should output exactly 7 features per employee-shift pair."""
        from app.ml.data_generator import generate_employees, generate_shift_history
        from app.ml.feature_engineer import FEATURE_COLS, compute_features

        employees = generate_employees()
        df = generate_shift_history(employees, noise_rate=0.02)
        featured = compute_features(df)

        assert len(FEATURE_COLS) == 7, f"Expected 7 feature columns, got {len(FEATURE_COLS)}"
        for col in FEATURE_COLS:
            assert col in featured.columns, f"Feature '{col}' should be in computed features"


# ---------------------------------------------------------------------------
# API Endpoint Smoke Tests
# ---------------------------------------------------------------------------

class TestAPISmoke:
    """Verify all major API endpoints return 200."""

    def test_health_check(self, client):
        """GET / returns healthy status."""
        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"

    def test_employees_endpoint(self, client, seed_employees):
        """GET /api/employees returns 200 with employee data."""
        resp = client.get("/api/employees")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_shifts_endpoint(self, client, seed_shifts):
        """GET /api/shifts returns 200 with shift data."""
        resp = client.get("/api/shifts")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_incidents_endpoint(self, client, seed_incidents):
        """GET /api/incidents returns 200 with incident data."""
        resp = client.get("/api/incidents")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_analytics_model_info(self, client, tmp_model_dir):
        """GET /api/analytics/model-info returns 200 when model exists."""
        from unittest.mock import patch

        from app.ml.train import train_model

        # Train model to a temp dir, then patch _ML_DIR so the endpoint finds it
        train_model(output_dir=tmp_model_dir)
        with patch("app.services.ml_service._ML_DIR", tmp_model_dir):
            # Clear the lru_cache so it picks up the patched path
            from app.services.ml_service import _load_metrics
            _load_metrics.cache_clear()
            resp = client.get("/api/analytics/model-info")
            _load_metrics.cache_clear()  # Clean up cache for other tests
        assert resp.status_code == 200
        data = resp.json()
        assert "roc_auc" in data

    def test_agent_status(self, client):
        """GET /api/agent/status returns 200 (Ollama may or may not be available)."""
        resp = client.get("/api/agent/status")
        assert resp.status_code == 200
        data = resp.json()
        assert "available" in data

    def test_recommendations_rank(self, client, seed_shifts, seed_employees):
        """POST /api/recommendations/rank returns 200 with ranked candidates."""
        from unittest.mock import patch

        def _mock_rank(shift, employees):
            return [
                {"employee_id": e.id, "name": e.name, "role": e.role,
                 "score": round(0.9 - i * 0.1, 4),
                 "reason": "Good match, Reliable, Available"}
                for i, e in enumerate(employees)
            ]

        with patch("app.routers.recommendations.ml_service.rank_candidates", side_effect=_mock_rank):
            resp = client.post("/api/recommendations/rank", json={"shift_id": 1})
        assert resp.status_code == 200
