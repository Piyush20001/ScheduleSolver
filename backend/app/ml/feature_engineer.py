"""Feature engineering for ScheduleSolver ML pipeline.

Extracts 7 features per employee-shift pair with point-in-time correctness.
No future data leaks: each feature uses only information available before the
current shift date.
"""

import numpy as np
import pandas as pd

FEATURE_COLS = [
    "preference_match",
    "skill_gap",
    "reliability_score",
    "hours_remaining",
    "is_weekend_match",
    "role_match",
    "days_since_last_shift",
]


def compute_features(df):
    """Extract 7 ML features from raw shift assignment data.

    Args:
        df: DataFrame from generate_shift_history() with columns including
            employee_id, employee_role, shift_date, shift_type, role_required,
            is_weekend, skill_level, min_skill_level, reliability_score,
            prefers_morning, prefers_evening, weekend_available,
            max_hours_weekly, accepted, week_number.

    Returns:
        DataFrame with FEATURE_COLS + "accepted" + "week_number" +
        "employee_id" + "shift_date" columns.
    """
    # Work on a copy sorted by date for point-in-time computation
    data = df.copy()
    data = data.sort_values(["shift_date", "employee_id"]).reset_index(drop=True)

    n = len(data)

    # Pre-allocate feature arrays
    pref_match = np.zeros(n, dtype=np.float64)
    skill_gap_arr = np.zeros(n, dtype=np.float64)
    reliability_arr = np.zeros(n, dtype=np.float64)
    hrs_remaining_arr = np.zeros(n, dtype=np.float64)
    wknd_match_arr = np.zeros(n, dtype=np.float64)
    role_match_arr = np.zeros(n, dtype=np.float64)
    days_since_arr = np.full(n, 7.0, dtype=np.float64)

    # Per-employee trackers for point-in-time computation
    # Two-level tracking to handle multiple rows on the same date:
    # - emp_prior_accepted: last accepted date strictly BEFORE current date
    # - emp_same_day_accepted: accepted dates to commit when date advances
    emp_prior_accepted = {}    # emp_id -> last accepted date (strictly < current date)
    emp_same_day_pending = {}  # emp_id -> accepted date to commit on next date change
    emp_week_hours = {}        # (emp_id, week_number) -> hours already assigned

    shift_hours = 8.0  # all shifts are 8 hours
    prev_date = None   # track date transitions

    # Extract columns as numpy arrays for faster access
    emp_ids = data["employee_id"].values
    emp_roles = data["employee_role"].values
    shift_dates = data["shift_date"].values
    shift_types = data["shift_type"].values
    roles_req = data["role_required"].values
    is_weekends = data["is_weekend"].values
    skill_levels = data["skill_level"].values
    min_skills = data["min_skill_level"].values
    reliabilities = data["reliability_score"].values
    pref_morns = data["prefers_morning"].values
    pref_eves = data["prefers_evening"].values
    wknd_avails = data["weekend_available"].values
    max_hrs_vals = data["max_hours_weekly"].values
    week_nums = data["week_number"].values
    accepted_vals = data["accepted"].values

    for i in range(n):
        emp_id = emp_ids[i]
        emp_role = emp_roles[i]
        s_date = shift_dates[i]
        s_type = shift_types[i]
        role_req = roles_req[i]
        is_wknd = is_weekends[i]
        emp_skill = skill_levels[i]
        min_skill = min_skills[i]
        rel = reliabilities[i]
        p_morn = pref_morns[i]
        p_eve = pref_eves[i]
        w_avail = wknd_avails[i]
        max_hrs = max_hrs_vals[i]
        week_num = week_nums[i]

        # When date advances, commit pending same-day acceptances to prior tracker
        if prev_date is not None and s_date != prev_date:
            for eid, d in emp_same_day_pending.items():
                curr = emp_prior_accepted.get(eid, None)
                if curr is None or d > curr:
                    emp_prior_accepted[eid] = d
            emp_same_day_pending.clear()
        prev_date = s_date

        # 1. preference_match (0-1)
        if s_type == "morning" and p_morn:
            pref_match[i] = 1.0
        elif s_type == "evening" and p_eve:
            pref_match[i] = 1.0
        elif s_type == "afternoon":
            pref_match[i] = 0.5
        elif not p_morn and not p_eve:
            pref_match[i] = 0.5
        else:
            pref_match[i] = 0.0

        # 2. skill_gap (employee skill - required skill)
        skill_gap_arr[i] = float(emp_skill - min_skill)

        # 3. reliability_score (direct from profile)
        reliability_arr[i] = rel

        # 4. hours_remaining (point-in-time within same week)
        key = (int(emp_id), int(week_num))
        hrs_used = emp_week_hours.get(key, 0.0)
        hrs_remaining_arr[i] = max(0.0, float(max_hrs) - hrs_used)

        # 5. is_weekend_match
        if is_wknd:
            wknd_match_arr[i] = 1.0 if w_avail else 0.0
        else:
            wknd_match_arr[i] = 0.5

        # 6. role_match (1.0 exact, 0.5 general fills, 0.0 incompatible)
        if emp_role == role_req:
            role_match_arr[i] = 1.0
        elif emp_role == "general" or role_req == "general":
            role_match_arr[i] = 0.5
        else:
            role_match_arr[i] = 0.0

        # 7. days_since_last_shift (point-in-time: only accepted strictly before this date)
        eid_key = int(emp_id)
        last_date = emp_prior_accepted.get(eid_key, None)
        if last_date is not None and s_date > last_date:
            days_since_arr[i] = float((s_date - last_date).days)
        else:
            days_since_arr[i] = 7.0  # default when no prior accepted assignments

        # Update trackers AFTER computing features for this row
        if accepted_vals[i] == 1:
            # Stage same-day acceptance for next date boundary commit
            curr_pending = emp_same_day_pending.get(eid_key, None)
            if curr_pending is None or s_date > curr_pending:
                emp_same_day_pending[eid_key] = s_date
            emp_week_hours[key] = hrs_used + shift_hours

    result = pd.DataFrame({
        "preference_match": pref_match,
        "skill_gap": skill_gap_arr,
        "reliability_score": reliability_arr,
        "hours_remaining": hrs_remaining_arr,
        "is_weekend_match": wknd_match_arr,
        "role_match": role_match_arr,
        "days_since_last_shift": days_since_arr,
        "accepted": data["accepted"].values,
        "week_number": data["week_number"].values,
        "employee_id": data["employee_id"].values,
        "shift_date": data["shift_date"].values,
    })

    return result
