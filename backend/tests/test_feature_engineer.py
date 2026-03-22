"""Tests for feature engineering module (ML-04, ML-05)."""

import numpy as np

from app.ml.data_generator import generate_employees, generate_shift_history
from app.ml.feature_engineer import FEATURE_COLS, compute_features


class TestFeatureCount:
    """ML-04: compute_features returns exactly 7 feature columns."""

    def test_feature_columns(self):
        emps = generate_employees()
        df = generate_shift_history(emps, n_weeks=12)
        featured = compute_features(df)
        for col in FEATURE_COLS:
            assert col in featured.columns, f"Missing feature column: {col}"

    def test_exactly_seven_features(self):
        expected = [
            "preference_match", "skill_gap", "reliability_score",
            "hours_remaining", "is_weekend_match", "role_match",
            "days_since_last_shift",
        ]
        assert FEATURE_COLS == expected, f"FEATURE_COLS mismatch: {FEATURE_COLS}"

    def test_accepted_column_preserved(self):
        emps = generate_employees()
        df = generate_shift_history(emps, n_weeks=12)
        featured = compute_features(df)
        assert "accepted" in featured.columns, "accepted column missing from output"

    def test_week_number_preserved(self):
        emps = generate_employees()
        df = generate_shift_history(emps, n_weeks=12)
        featured = compute_features(df)
        assert "week_number" in featured.columns, "week_number column missing from output"


class TestFeatureValuesRange:
    """All features produce valid numeric values."""

    def test_no_nan(self):
        emps = generate_employees()
        df = generate_shift_history(emps, n_weeks=12)
        featured = compute_features(df)
        nan_counts = featured[FEATURE_COLS].isna().sum()
        assert nan_counts.sum() == 0, f"NaN values found:\n{nan_counts[nan_counts > 0]}"

    def test_no_infinity(self):
        emps = generate_employees()
        df = generate_shift_history(emps, n_weeks=12)
        featured = compute_features(df)
        for col in FEATURE_COLS:
            assert np.isfinite(featured[col]).all(), f"Infinity values in {col}"

    def test_preference_match_range(self):
        emps = generate_employees()
        df = generate_shift_history(emps, n_weeks=12)
        featured = compute_features(df)
        assert featured["preference_match"].min() >= 0.0
        assert featured["preference_match"].max() <= 1.0

    def test_reliability_score_range(self):
        emps = generate_employees()
        df = generate_shift_history(emps, n_weeks=12)
        featured = compute_features(df)
        assert featured["reliability_score"].min() >= 0.0
        assert featured["reliability_score"].max() <= 1.0


class TestNoFutureLeak:
    """ML-05: Point-in-time correctness for days_since_last_shift."""

    def test_no_future_data(self):
        emps = generate_employees()
        df = generate_shift_history(emps, n_weeks=12)
        featured = compute_features(df)

        # For a sample of rows, verify days_since_last_shift
        # uses only assignments before the row's date
        sample_size = min(50, len(featured))
        rng = np.random.RandomState(123)
        sample_idx = rng.choice(len(featured), sample_size, replace=False)

        for idx in sample_idx:
            row = featured.iloc[idx]
            emp_id = row.get("employee_id", None)
            if emp_id is None:
                # If employee_id is not in featured, check via original df
                continue

            shift_date = row.get("shift_date", None)
            if shift_date is None:
                continue

            # Get all accepted assignments for this employee before this date
            mask = (
                (df["employee_id"] == emp_id)
                & (df["shift_date"] < shift_date)
                & (df["accepted"] == 1)
            )
            prior = df.loc[mask, "shift_date"]

            if len(prior) == 0:
                expected = 7.0  # default when no prior assignments
            else:
                last_date = prior.max()
                expected = (shift_date - last_date).days

            actual = row["days_since_last_shift"]
            assert actual == expected, (
                f"Row {idx}: days_since_last_shift={actual} but expected {expected} "
                f"(emp={emp_id}, date={shift_date})"
            )
