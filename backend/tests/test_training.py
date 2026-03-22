"""Tests for XGBoost training pipeline (ML-06, ML-07, ML-08).

Integration tests that run the full data generation + training pipeline.
Each test uses a temporary directory for model artifacts to avoid side effects.
"""

import json
import os

import joblib
import numpy as np
import pytest

from app.ml.train import train_model


@pytest.fixture
def trained_artifacts(tmp_model_dir):
    """Train model once and return (metrics_dict, output_dir) for reuse."""
    metrics = train_model(output_dir=tmp_model_dir)
    return metrics, tmp_model_dir


class TestTrainingPipeline:
    """XGBoost training pipeline tests."""

    def test_roc_auc_threshold(self, trained_artifacts):
        """ML-06: Model achieves 98%+ ROC-AUC on temporal test set (weeks 11-12)."""
        metrics, output_dir = trained_artifacts
        metrics_path = os.path.join(output_dir, "metrics.json")
        assert os.path.exists(metrics_path)
        with open(metrics_path) as f:
            saved = json.load(f)
        assert saved["roc_auc"] >= 0.98, f"ROC-AUC {saved['roc_auc']} < 0.98"

    def test_metrics_file(self, trained_artifacts):
        """ML-07: metrics.json contains all required keys."""
        _, output_dir = trained_artifacts
        metrics_path = os.path.join(output_dir, "metrics.json")
        with open(metrics_path) as f:
            saved = json.load(f)
        # Required top-level keys
        for key in ["roc_auc", "accuracy", "precision", "recall", "confusion_matrix", "feature_importances"]:
            assert key in saved, f"Missing key: {key}"
        # Confusion matrix has tn/fp/fn/tp
        cm = saved["confusion_matrix"]
        for key in ["tn", "fp", "fn", "tp"]:
            assert key in cm, f"Missing confusion_matrix key: {key}"
        # Feature importances is a dict with feature names
        fi = saved["feature_importances"]
        assert isinstance(fi, dict)
        assert len(fi) >= 5, f"Expected 5+ features, got {len(fi)}"

    def test_model_persistence(self, trained_artifacts):
        """ML-08: model.pkl is loadable and can predict."""
        _, output_dir = trained_artifacts
        model_path = os.path.join(output_dir, "model.pkl")
        assert os.path.exists(model_path)
        model = joblib.load(model_path)
        # Create sample data with 7 features matching FEATURE_COLS
        sample = np.array([[0.8, 2.0, 0.9, 24.0, 1.0, 1.0, 3.0]])
        proba = model.predict_proba(sample)
        assert proba.shape == (1, 2), f"Expected shape (1, 2), got {proba.shape}"

    def test_feature_importances_order(self, trained_artifacts):
        """reliability_score and preference_match are top 2 features by importance."""
        _, output_dir = trained_artifacts
        metrics_path = os.path.join(output_dir, "metrics.json")
        with open(metrics_path) as f:
            saved = json.load(f)
        fi = saved["feature_importances"]
        # Sort features by importance descending
        sorted_features = sorted(fi.items(), key=lambda x: x[1], reverse=True)
        top_2_names = {sorted_features[0][0], sorted_features[1][0]}
        assert "reliability_score" in top_2_names, (
            f"reliability_score not in top 2: {sorted_features[:3]}"
        )
        assert "preference_match" in top_2_names, (
            f"preference_match not in top 2: {sorted_features[:3]}"
        )

    def test_console_output(self, tmp_model_dir, capsys):
        """ML-07: Console output contains ROC-AUC and uses [INFO]/[OK] prefixes."""
        train_model(output_dir=tmp_model_dir)
        captured = capsys.readouterr()
        assert "[OK]" in captured.out, "Missing [OK] prefix in output"
        assert "ROC-AUC" in captured.out, "Missing ROC-AUC in output"
        assert "[INFO]" in captured.out, "Missing [INFO] prefix in output"

    def test_temporal_split(self, trained_artifacts):
        """Training uses weeks 1-10, testing uses weeks 11-12 (no overlap)."""
        metrics, output_dir = trained_artifacts
        metrics_path = os.path.join(output_dir, "metrics.json")
        with open(metrics_path) as f:
            saved = json.load(f)
        # Verify train/test split metadata
        assert saved.get("train_weeks") == "1-10", f"Train weeks: {saved.get('train_weeks')}"
        assert saved.get("test_weeks") == "11-12", f"Test weeks: {saved.get('test_weeks')}"
