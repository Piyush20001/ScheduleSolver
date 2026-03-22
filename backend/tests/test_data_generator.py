"""Tests for synthetic data generator (ML-01, ML-02, ML-03)."""

import numpy as np

from app.ml.data_generator import generate_employees, generate_shift_history, inject_noise


VALID_ROLES = {"cook", "server", "cashier", "host", "manager", "barista", "general"}
REQUIRED_EMP_FIELDS = {
    "name", "email", "phone", "role", "skill_level", "reliability_score",
    "prefers_morning", "prefers_evening", "weekend_available",
    "max_hours_weekly", "hired_date",
}


class TestEmployeeGeneration:
    """ML-01: Synthetic data generator produces ~25 employees."""

    def test_employee_count(self):
        emps = generate_employees()
        assert 20 <= len(emps) <= 30, f"Expected ~25 employees, got {len(emps)}"

    def test_required_fields(self):
        emps = generate_employees()
        for emp in emps:
            missing = REQUIRED_EMP_FIELDS - set(emp.keys())
            assert not missing, f"Employee {emp.get('name', '?')} missing fields: {missing}"

    def test_valid_roles(self):
        emps = generate_employees()
        for emp in emps:
            assert emp["role"] in VALID_ROLES, f"Invalid role: {emp['role']}"

    def test_no_duplicate_names(self):
        emps = generate_employees()
        names = [e["name"] for e in emps]
        assert len(names) == len(set(names)), "Duplicate employee names found"

    def test_no_duplicate_emails(self):
        emps = generate_employees()
        emails = [e["email"] for e in emps]
        assert len(emails) == len(set(emails)), "Duplicate employee emails found"


class TestEmployeeDiversity:
    """ML-01: Employee profiles are realistic and diverse."""

    def test_reliability_distribution(self):
        emps = generate_employees()
        scores = [e["reliability_score"] for e in emps]
        # Most should be in 0.6-0.85 range
        mid_range = [s for s in scores if 0.6 <= s <= 0.85]
        assert len(mid_range) >= len(emps) * 0.4, "Too few employees in mid-range reliability"
        # Some stars (0.9+)
        stars = [s for s in scores if s >= 0.9]
        assert len(stars) >= 1, "Should have at least 1 star employee (0.9+)"
        # Some unreliable (0.3-0.5)
        low = [s for s in scores if 0.3 <= s <= 0.5]
        assert len(low) >= 1, "Should have at least 1 unreliable employee (0.3-0.5)"

    def test_role_diversity(self):
        emps = generate_employees()
        roles = set(e["role"] for e in emps)
        # Should have at least 5 different roles
        assert len(roles) >= 5, f"Too few distinct roles: {roles}"

    def test_skill_levels_valid(self):
        emps = generate_employees()
        for emp in emps:
            assert 1 <= emp["skill_level"] <= 5, f"Skill level out of range: {emp['skill_level']}"


class TestAssignmentVolume:
    """ML-02: Generator produces 12+ weeks with 5000-8000 records."""

    def test_record_count(self):
        emps = generate_employees()
        df = generate_shift_history(emps, n_weeks=12)
        assert 5000 <= len(df) <= 8000, f"Expected 5000-8000 rows, got {len(df)}"

    def test_has_required_columns(self):
        emps = generate_employees()
        df = generate_shift_history(emps, n_weeks=12)
        required = {"employee_id", "shift_date", "week_number", "shift_type",
                     "role_required", "is_weekend", "accepted"}
        missing = required - set(df.columns)
        assert not missing, f"Missing columns: {missing}"

    def test_week_coverage(self):
        emps = generate_employees()
        df = generate_shift_history(emps, n_weeks=12)
        weeks = df["week_number"].unique()
        assert len(weeks) >= 12, f"Expected 12+ weeks, got {len(weeks)}"


class TestShiftTypes:
    """Shift types and weekend marking."""

    def test_shift_types_present(self):
        emps = generate_employees()
        df = generate_shift_history(emps, n_weeks=12)
        types = set(df["shift_type"].unique())
        expected = {"morning", "afternoon", "evening"}
        assert expected.issubset(types), f"Missing shift types: {expected - types}"

    def test_weekend_marking(self):
        emps = generate_employees()
        df = generate_shift_history(emps, n_weeks=12)
        # Should have both weekend and non-weekend shifts
        assert df["is_weekend"].any(), "No weekend shifts found"
        assert not df["is_weekend"].all(), "All shifts marked as weekend"


class TestNoiseInjection:
    """ML-03: ~10% label noise injection."""

    def test_noise_rate(self):
        labels = np.ones(1000, dtype=int)
        noisy = inject_noise(labels, noise_rate=0.10, seed=42)
        flip_rate = (labels != noisy).mean()
        assert 0.07 <= flip_rate <= 0.13, f"Noise rate {flip_rate:.3f} outside 7-13% tolerance"

    def test_noise_deterministic(self):
        labels = np.ones(1000, dtype=int)
        noisy1 = inject_noise(labels, noise_rate=0.10, seed=42)
        noisy2 = inject_noise(labels, noise_rate=0.10, seed=42)
        np.testing.assert_array_equal(noisy1, noisy2, "Noise should be deterministic with same seed")


class TestClassBalance:
    """After noise injection, positive class ratio is ~60-70%."""

    def test_positive_ratio(self):
        emps = generate_employees()
        df = generate_shift_history(emps, n_weeks=12)
        pos_ratio = df["accepted"].mean()
        assert 0.50 <= pos_ratio <= 0.80, f"Positive ratio {pos_ratio:.3f} outside 50-80% range"
