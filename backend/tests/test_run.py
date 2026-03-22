"""Tests for run.py entry point (DATA-04)."""

import os
import subprocess
import sys
import time

import pytest


@pytest.fixture
def clean_backend_dir():
    """Create a temp copy-like environment and clean up artifacts."""
    # We run against the actual backend dir but clean up artifacts after
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.path.join(backend_dir, "app", "ml", "model.pkl")
    metrics_path = os.path.join(backend_dir, "app", "ml", "metrics.json")
    data_dir = os.path.join(backend_dir, "data")
    db_path = os.path.join(data_dir, "schedulesolver.db")

    # Remove artifacts if they exist (ensure fresh first run)
    for f in [model_path, metrics_path, db_path]:
        if os.path.exists(f):
            os.remove(f)

    yield backend_dir

    # Cleanup after test
    for f in [model_path, metrics_path, db_path]:
        if os.path.exists(f):
            os.remove(f)


class TestRunPy:
    """run.py entry point tests."""

    def test_first_run_flow(self, clean_backend_dir):
        """DATA-04: First run creates model.pkl, database, prints [INFO]."""
        result = subprocess.run(
            [sys.executable, "run.py", "--no-serve"],
            cwd=clean_backend_dir,
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0, f"run.py failed:\n{result.stderr}"
        # Check artifacts created
        assert os.path.exists(
            os.path.join(clean_backend_dir, "app", "ml", "model.pkl")
        ), "model.pkl not created"
        assert os.path.exists(
            os.path.join(clean_backend_dir, "data", "schedulesolver.db")
        ), "schedulesolver.db not created"
        # Check console output
        assert "[INFO] First run detected" in result.stdout
        assert "[OK]" in result.stdout
        assert "ROC-AUC" in result.stdout

    def test_subsequent_run_skips(self, clean_backend_dir):
        """DATA-04: Second run skips training/seeding, boots fast."""
        # First run
        subprocess.run(
            [sys.executable, "run.py", "--no-serve"],
            cwd=clean_backend_dir,
            capture_output=True,
            text=True,
            timeout=60,
        )
        # Second run
        start = time.time()
        result = subprocess.run(
            [sys.executable, "run.py", "--no-serve"],
            cwd=clean_backend_dir,
            capture_output=True,
            text=True,
            timeout=30,
        )
        elapsed = time.time() - start
        assert result.returncode == 0, f"Second run failed:\n{result.stderr}"
        assert "[OK]" in result.stdout
        assert "Model loaded" in result.stdout
        assert "Training XGBoost" not in result.stdout
        assert elapsed < 10, f"Second run took {elapsed:.1f}s, expected < 10s"
