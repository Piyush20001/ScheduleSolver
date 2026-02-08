"""Synthetic data generator for ScheduleSolver ML pipeline.

Produces ~25 hardcoded employee profiles and 12+ weeks of shift assignment
history with ~10% label noise for XGBoost training.
"""

from datetime import date, timedelta

import numpy as np
import pandas as pd


# Hardcoded employee profiles -- diverse, realistic food service team
# modeled after a University of Florida dining operation (~25 staff).
EMPLOYEES = [
    # Servers (~5)
    {"name": "Sarah Chen", "email": "sarah.chen@schedulesolvermail.com", "phone": "352-555-0101",
     "role": "server", "skill_level": 4, "reliability_score": 0.92,
     "prefers_morning": True, "prefers_evening": False, "weekend_available": True,
     "max_hours_weekly": 35, "hired_date": date(2023, 8, 15)},
    {"name": "Marcus Johnson", "email": "marcus.johnson@schedulesolvermail.com", "phone": "352-555-0102",
     "role": "server", "skill_level": 3, "reliability_score": 0.78,
     "prefers_morning": False, "prefers_evening": True, "weekend_available": False,
     "max_hours_weekly": 25, "hired_date": date(2024, 1, 10)},
    {"name": "Aisha Williams", "email": "aisha.williams@schedulesolvermail.com", "phone": "352-555-0103",
     "role": "server", "skill_level": 3, "reliability_score": 0.81,
     "prefers_morning": True, "prefers_evening": False, "weekend_available": True,
     "max_hours_weekly": 30, "hired_date": date(2023, 5, 20)},
    {"name": "Tyler Brooks", "email": "tyler.brooks@schedulesolvermail.com", "phone": "352-555-0104",
     "role": "server", "skill_level": 2, "reliability_score": 0.65,
     "prefers_morning": False, "prefers_evening": True, "weekend_available": True,
     "max_hours_weekly": 20, "hired_date": date(2024, 8, 1)},
    {"name": "Mei-Lin Wu", "email": "mei-lin.wu@schedulesolvermail.com", "phone": "352-555-0105",
     "role": "server", "skill_level": 3, "reliability_score": 0.74,
     "prefers_morning": True, "prefers_evening": False, "weekend_available": False,
     "max_hours_weekly": 30, "hired_date": date(2024, 3, 12)},

    # Cooks (~4)
    {"name": "Diego Rivera", "email": "diego.rivera@schedulesolvermail.com", "phone": "352-555-0201",
     "role": "cook", "skill_level": 5, "reliability_score": 0.91,
     "prefers_morning": True, "prefers_evening": False, "weekend_available": True,
     "max_hours_weekly": 40, "hired_date": date(2022, 6, 1)},
    {"name": "Kenji Nakamura", "email": "kenji.nakamura@schedulesolvermail.com", "phone": "352-555-0202",
     "role": "cook", "skill_level": 4, "reliability_score": 0.83,
     "prefers_morning": True, "prefers_evening": False, "weekend_available": True,
     "max_hours_weekly": 35, "hired_date": date(2023, 2, 14)},
    {"name": "Fatima Al-Rashid", "email": "fatima.al-rashid@schedulesolvermail.com", "phone": "352-555-0203",
     "role": "cook", "skill_level": 3, "reliability_score": 0.72,
     "prefers_morning": False, "prefers_evening": True, "weekend_available": False,
     "max_hours_weekly": 30, "hired_date": date(2024, 5, 20)},
    {"name": "Andre Washington", "email": "andre.washington@schedulesolvermail.com", "phone": "352-555-0204",
     "role": "cook", "skill_level": 3, "reliability_score": 0.45,
     "prefers_morning": False, "prefers_evening": True, "weekend_available": True,
     "max_hours_weekly": 25, "hired_date": date(2024, 9, 5)},

    # Cashiers (~3)
    {"name": "Priya Patel", "email": "priya.patel@schedulesolvermail.com", "phone": "352-555-0301",
     "role": "cashier", "skill_level": 3, "reliability_score": 0.88,
     "prefers_morning": True, "prefers_evening": False, "weekend_available": True,
     "max_hours_weekly": 30, "hired_date": date(2023, 9, 1)},
    {"name": "Jordan Taylor", "email": "jordan.taylor@schedulesolvermail.com", "phone": "352-555-0302",
     "role": "cashier", "skill_level": 2, "reliability_score": 0.67,
     "prefers_morning": False, "prefers_evening": True, "weekend_available": False,
     "max_hours_weekly": 20, "hired_date": date(2024, 6, 15)},
    {"name": "Sofia Martinez", "email": "sofia.martinez@schedulesolvermail.com", "phone": "352-555-0303",
     "role": "cashier", "skill_level": 3, "reliability_score": 0.79,
     "prefers_morning": True, "prefers_evening": False, "weekend_available": True,
     "max_hours_weekly": 25, "hired_date": date(2024, 1, 22)},

    # Baristas (~3)
    {"name": "Liam O'Brien", "email": "liam.obrien@schedulesolvermail.com", "phone": "352-555-0401",
     "role": "barista", "skill_level": 4, "reliability_score": 0.85,
     "prefers_morning": True, "prefers_evening": False, "weekend_available": False,
     "max_hours_weekly": 30, "hired_date": date(2023, 11, 1)},
    {"name": "Zara Ahmed", "email": "zara.ahmed@schedulesolvermail.com", "phone": "352-555-0402",
     "role": "barista", "skill_level": 3, "reliability_score": 0.76,
     "prefers_morning": False, "prefers_evening": True, "weekend_available": True,
     "max_hours_weekly": 25, "hired_date": date(2024, 4, 10)},
    {"name": "Noah Kim", "email": "noah.kim@schedulesolvermail.com", "phone": "352-555-0403",
     "role": "barista", "skill_level": 2, "reliability_score": 0.38,
     "prefers_morning": False, "prefers_evening": True, "weekend_available": False,
     "max_hours_weekly": 20, "hired_date": date(2024, 10, 1)},

    # Hosts (~3)
    {"name": "Emma Rodriguez", "email": "emma.rodriguez@schedulesolvermail.com", "phone": "352-555-0501",
     "role": "host", "skill_level": 3, "reliability_score": 0.82,
     "prefers_morning": True, "prefers_evening": False, "weekend_available": True,
     "max_hours_weekly": 25, "hired_date": date(2023, 7, 15)},
    {"name": "David Okafor", "email": "david.okafor@schedulesolvermail.com", "phone": "352-555-0502",
     "role": "host", "skill_level": 2, "reliability_score": 0.71,
     "prefers_morning": False, "prefers_evening": True, "weekend_available": True,
     "max_hours_weekly": 20, "hired_date": date(2024, 2, 28)},
    {"name": "Lily Tran", "email": "lily.tran@schedulesolvermail.com", "phone": "352-555-0503",
     "role": "host", "skill_level": 2, "reliability_score": 0.63,
     "prefers_morning": True, "prefers_evening": False, "weekend_available": False,
     "max_hours_weekly": 20, "hired_date": date(2024, 7, 8)},

    # Managers (~2)
    {"name": "Robert Chang", "email": "robert.chang@schedulesolvermail.com", "phone": "352-555-0601",
     "role": "manager", "skill_level": 5, "reliability_score": 0.95,
     "prefers_morning": True, "prefers_evening": False, "weekend_available": True,
     "max_hours_weekly": 40, "hired_date": date(2022, 1, 15)},
    {"name": "Jessica Barnes", "email": "jessica.barnes@schedulesolvermail.com", "phone": "352-555-0602",
     "role": "manager", "skill_level": 4, "reliability_score": 0.90,
     "prefers_morning": False, "prefers_evening": True, "weekend_available": True,
     "max_hours_weekly": 40, "hired_date": date(2022, 9, 1)},

    # General (~5)
    {"name": "Chris Morales", "email": "chris.morales@schedulesolvermail.com", "phone": "352-555-0701",
     "role": "general", "skill_level": 2, "reliability_score": 0.70,
     "prefers_morning": True, "prefers_evening": False, "weekend_available": True,
     "max_hours_weekly": 30, "hired_date": date(2024, 3, 1)},
    {"name": "Jasmine Lee", "email": "jasmine.lee@schedulesolvermail.com", "phone": "352-555-0702",
     "role": "general", "skill_level": 1, "reliability_score": 0.60,
     "prefers_morning": False, "prefers_evening": True, "weekend_available": False,
     "max_hours_weekly": 20, "hired_date": date(2024, 8, 20)},
    {"name": "Ryan Cooper", "email": "ryan.cooper@schedulesolvermail.com", "phone": "352-555-0703",
     "role": "general", "skill_level": 2, "reliability_score": 0.73,
     "prefers_morning": True, "prefers_evening": False, "weekend_available": True,
     "max_hours_weekly": 25, "hired_date": date(2024, 5, 1)},
    {"name": "Olivia Nguyen", "email": "olivia.nguyen@schedulesolvermail.com", "phone": "352-555-0704",
     "role": "general", "skill_level": 1, "reliability_score": 0.35,
     "prefers_morning": False, "prefers_evening": False, "weekend_available": True,
     "max_hours_weekly": 20, "hired_date": date(2024, 11, 10)},
    {"name": "Ethan Park", "email": "ethan.park@schedulesolvermail.com", "phone": "352-555-0705",
     "role": "general", "skill_level": 2, "reliability_score": 0.68,
     "prefers_morning": True, "prefers_evening": False, "weekend_available": False,
     "max_hours_weekly": 25, "hired_date": date(2024, 6, 1)},
]

# Role compatibility: general can fill any role
COMPATIBLE_ROLES = {
    "server": {"server", "general"},
    "cook": {"cook", "general"},
    "cashier": {"cashier", "general"},
    "barista": {"barista", "general"},
    "host": {"host", "general"},
    "manager": {"manager"},
    "general": {"server", "cook", "cashier", "barista", "host", "general"},
}

# Shift definitions
SHIFT_DEFS = {
    "morning":   {"start": "06:00", "end": "14:00", "hours": 8},
    "afternoon": {"start": "14:00", "end": "22:00", "hours": 8},
    "evening":   {"start": "22:00", "end": "06:00", "hours": 8},
}

# Roles that can be demanded for shift slots (weighted pool for random selection)
_ROLE_POOL = (
    ["server"] * 4
    + ["cook"] * 4
    + ["cashier"] * 2
    + ["barista"] * 2
    + ["host"] * 2
    + ["manager"] * 1
)

# Each shift period picks 3 roles from this pool
_ROLES_PER_SHIFT = 3


def generate_employees():
    """Return list of ~25 hardcoded employee profile dicts."""
    return [dict(emp) for emp in EMPLOYEES]


def inject_noise(labels, noise_rate=0.10, seed=42):
    """Flip ~noise_rate fraction of binary labels randomly.

    Args:
        labels: numpy array of 0/1 values.
        noise_rate: fraction of labels to flip (default 10%).
        seed: random seed for reproducibility.

    Returns:
        numpy array with ~noise_rate labels flipped.
    """
    rng = np.random.RandomState(seed)
    noisy = labels.copy()
    flip_mask = rng.random(len(labels)) < noise_rate
    noisy[flip_mask] = 1 - noisy[flip_mask]
    return noisy


def generate_shift_history(employees, n_weeks=12, seed=42, noise_rate=0.10):
    """Generate synthetic shift assignment outcome records.

    Creates 3 shifts per day (morning/afternoon/evening) for n_weeks weeks,
    assigns roles to each shift based on demand weights, evaluates all
    compatible employees, computes a deterministic acceptance score, and
    injects label noise.

    Args:
        employees: list of employee dicts from generate_employees().
        n_weeks: number of weeks of history (default 12).
        seed: random seed for reproducibility.
        noise_rate: fraction of labels to flip (default 0.10).

    Returns:
        DataFrame with columns: employee_id, employee_name, shift_date,
        week_number, shift_type, role_required, is_weekend,
        skill_level, min_skill_level, reliability_score,
        prefers_morning, prefers_evening, weekend_available,
        max_hours_weekly, accepted
    """
    rng = np.random.RandomState(seed)

    # Build employee lookup with integer IDs (1-indexed)
    emp_lookup = {}
    for i, emp in enumerate(employees):
        emp_lookup[i + 1] = emp

    # Generate shift schedule: 3 shifts/day * 7 days/week * n_weeks
    # Start from a Monday 12 weeks ago relative to a fixed anchor
    anchor = date(2025, 1, 6)  # a Monday
    start_date = anchor

    records = []

    for week in range(n_weeks):
        # Track hours assigned per employee this week (point-in-time)
        week_hours = {eid: 0.0 for eid in emp_lookup}

        for day_offset in range(7):
            current_date = start_date + timedelta(weeks=week, days=day_offset)
            day_of_week = current_date.weekday()  # 0=Mon, 6=Sun
            is_weekend = day_of_week >= 5

            for shift_type in ["morning", "afternoon", "evening"]:
                shift_def = SHIFT_DEFS[shift_type]
                shift_hours = shift_def["hours"]

                # Each shift period demands a random subset of roles
                shift_roles = list(rng.choice(
                    _ROLE_POOL, size=_ROLES_PER_SHIFT, replace=False
                ))

                for role_required in shift_roles:
                    min_skill = 1 if role_required in ("general", "host") else rng.choice([1, 2], p=[0.7, 0.3])

                    # Evaluate each compatible employee
                    for eid, emp in emp_lookup.items():
                        # Check role compatibility
                        compatible = COMPATIBLE_ROLES.get(role_required, set())
                        if emp["role"] not in compatible:
                            continue

                        # Compute deterministic acceptance score
                        # preference_match
                        if shift_type == "morning" and emp["prefers_morning"]:
                            pref_match = 1.0
                        elif shift_type == "evening" and emp["prefers_evening"]:
                            pref_match = 1.0
                        elif shift_type == "afternoon":
                            pref_match = 0.5  # neutral
                        elif (shift_type == "morning" and not emp["prefers_morning"]) or \
                             (shift_type == "evening" and not emp["prefers_evening"]):
                            pref_match = 0.0 if (emp["prefers_morning"] or emp["prefers_evening"]) else 0.5
                        else:
                            pref_match = 0.5

                        # skill match
                        skill_gap = emp["skill_level"] - min_skill
                        skill_score = min(1.0, max(0.0, 0.5 + skill_gap * 0.15))

                        # reliability
                        rel = emp["reliability_score"]

                        # hours remaining
                        hrs_remaining = emp["max_hours_weekly"] - week_hours[eid]
                        hrs_score = min(1.0, max(0.0, hrs_remaining / emp["max_hours_weekly"]))

                        # weekend match
                        if is_weekend:
                            wknd_match = 1.0 if emp["weekend_available"] else 0.0
                        else:
                            wknd_match = 0.5

                        # Weighted acceptance score
                        score = (
                            0.30 * rel
                            + 0.25 * pref_match
                            + 0.20 * skill_score
                            + 0.15 * hrs_score
                            + 0.10 * wknd_match
                        )

                        # Deterministic threshold (tuned for ~65% positive ratio)
                        accepted = 1 if score > 0.45 else 0

                        records.append({
                            "employee_id": eid,
                            "employee_name": emp["name"],
                            "employee_role": emp["role"],
                            "shift_date": current_date,
                            "week_number": week + 1,
                            "shift_type": shift_type,
                            "role_required": role_required,
                            "is_weekend": is_weekend,
                            "skill_level": emp["skill_level"],
                            "min_skill_level": min_skill,
                            "reliability_score": rel,
                            "prefers_morning": emp["prefers_morning"],
                            "prefers_evening": emp["prefers_evening"],
                            "weekend_available": emp["weekend_available"],
                            "max_hours_weekly": emp["max_hours_weekly"],
                            "accepted": accepted,
                        })

                        # If accepted, accumulate hours for this week
                        if accepted == 1:
                            week_hours[eid] += shift_hours

    df = pd.DataFrame(records)

    # Inject label noise
    noisy_labels = inject_noise(df["accepted"].values, noise_rate=noise_rate, seed=seed)
    df.loc[:, "accepted"] = noisy_labels

    return df
