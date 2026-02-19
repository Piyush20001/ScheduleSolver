"""ML service: model loading, candidate ranking, and reason generation.

Loads the trained XGBoost model and metrics.json, ranks employees for
a given shift using ML inference, and generates human-readable reason
strings from the top 3 contributing features.
"""

import functools
import json
import os

import joblib
import pandas as pd

from app.ml.feature_engineer import FEATURE_COLS, compute_features

# Directory containing model.pkl and metrics.json
_ML_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ml")


@functools.lru_cache(maxsize=1)
def _load_model():
    """Load the trained XGBoost model from disk (cached)."""
    model_path = os.path.join(_ML_DIR, "model.pkl")
    return joblib.load(model_path)


@functools.lru_cache(maxsize=1)
def _load_metrics():
    """Load metrics.json from disk (cached)."""
    metrics_path = os.path.join(_ML_DIR, "metrics.json")
    with open(metrics_path) as f:
        return json.load(f)


def get_model():
    """Public wrapper for model loading."""
    return _load_model()


def get_metrics():
    """Public wrapper for metrics loading."""
    return _load_metrics()


# Human-readable labels keyed by feature name.
# Each entry: (threshold_check_func, label_text) tuples evaluated top-down.
# Returns (label_text, include?) -- None means skip this feature.
def _preference_label(val):
    if val >= 0.8:
        return "Strong preference match"
    if val <= 0.2:
        return "Preference mismatch"
    return None


def _skill_gap_label(val):
    if val > 0:
        return f"Skill level +{int(val)} above required"
    if val == 0:
        return "Meets skill requirement"
    return None


def _reliability_label(val):
    if val >= 0.8:
        return f"High reliability ({val:.2f})"
    if val >= 0.5:
        return f"Moderate reliability ({val:.2f})"
    return None


def _hours_remaining_label(val):
    if val > 0:
        return f"{int(val)} hrs remaining this week"
    return None


def _weekend_match_label(val):
    if val >= 0.8:
        return "Weekend available"
    return None


def _role_match_label(val):
    if val >= 0.9:
        return "Exact role match"
    if val >= 0.4:
        return "Compatible role"
    return None


def _days_since_label(val):
    if val >= 7:
        return "Well-rested (7+ days)"
    if val < 3:
        return f"Recent shift ({int(val)}d ago)"
    return None


_FEATURE_LABEL_FUNCS = {
    "preference_match": _preference_label,
    "skill_gap": _skill_gap_label,
    "reliability_score": _reliability_label,
    "hours_remaining": _hours_remaining_label,
    "is_weekend_match": _weekend_match_label,
    "role_match": _role_match_label,
    "days_since_last_shift": _days_since_label,
}

# Neutral fallback labels for when fewer than 3 primary labels match
_FALLBACK_LABELS = [
    "Available this week",
    "Standard scheduling fit",
    "General availability",
]


def _generate_reason(feature_values, feature_importances):
    """Generate a human-readable reason string from top 3 contributing features.

    Args:
        feature_values: dict mapping feature name -> float value for this candidate.
        feature_importances: dict mapping feature name -> float importance from model.

    Returns:
        String with exactly 3 comma-separated descriptive phrases.
    """
    # Generate labels for each feature, weighted by importance
    scored_labels = []
    for feat_name in FEATURE_COLS:
        label_func = _FEATURE_LABEL_FUNCS.get(feat_name)
        if label_func is None:
            continue
        val = feature_values.get(feat_name, 0.0)
        label = label_func(val)
        if label is not None:
            importance = feature_importances.get(feat_name, 0.0)
            scored_labels.append((importance, label))

    # Sort by importance descending, take top 3
    scored_labels.sort(key=lambda x: x[0], reverse=True)
    labels = [label for _, label in scored_labels[:3]]

    # Fill remaining slots with fallbacks to always have exactly 3
    fallback_idx = 0
    while len(labels) < 3 and fallback_idx < len(_FALLBACK_LABELS):
        labels.append(_FALLBACK_LABELS[fallback_idx])
        fallback_idx += 1

    return ", ".join(labels[:3])


def rank_candidates(shift, employees):
    """Rank employees for a shift using ML inference.

    Args:
        shift: Shift ORM object (the shift to fill).
        employees: list of Employee ORM objects (already filtered for role compatibility).

    Returns:
        List of dicts sorted by score descending:
        [{employee_id, name, role, score, reason}, ...]
    """
    if not employees:
        return []

    model = get_model()
    metrics = get_metrics()
    feature_importances = metrics.get("feature_importances", {})

    # Build DataFrame matching compute_features() input schema
    rows = []
    for emp in employees:
        # Extract week_number from shift date
        week_number = shift.date.isocalendar()[1]

        rows.append({
            "employee_id": emp.id,
            "employee_role": emp.role,
            "shift_date": shift.date,
            "week_number": week_number,
            "shift_type": shift.shift_type,
            "role_required": shift.role_required,
            "is_weekend": shift.is_weekend,
            "skill_level": emp.skill_level,
            "min_skill_level": shift.min_skill_level,
            "reliability_score": emp.reliability_score,
            "prefers_morning": emp.prefers_morning,
            "prefers_evening": emp.prefers_evening,
            "weekend_available": emp.weekend_available,
            "max_hours_weekly": emp.max_hours_weekly,
            "accepted": 0,  # placeholder -- not used for inference
        })

    df = pd.DataFrame(rows)
    features_df = compute_features(df)

    # Extract feature matrix and predict
    X = features_df[FEATURE_COLS].values
    scores = model.predict_proba(X)[:, 1]

    # Build result list with reasons
    results = []
    for i, emp in enumerate(employees):
        # Extract feature values for this candidate
        feature_vals = {col: float(features_df.iloc[i][col]) for col in FEATURE_COLS}
        reason = _generate_reason(feature_vals, feature_importances)

        results.append({
            "employee_id": emp.id,
            "name": emp.name,
            "role": emp.role,
            "score": round(float(scores[i]), 4),
            "reason": reason,
        })

    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    return results
