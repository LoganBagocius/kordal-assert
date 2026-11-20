from .types import Failure

SIDE_EFFECTS = frozenset({"issue_refund", "approve", "update_record"})
TRACKED_FIELDS = ("age_days", "effective_date")
OVERRIDE_KEYS = ("override", "human_approved")


def _data(step):
    data = step.get("data")
    return data if isinstance(data, dict) else {}


def _is_side_effect(step):
    return step.get("step") in SIDE_EFFECTS


def _first_side_effect_after(steps, index):
    for j in range(index + 1, len(steps)):
        if _is_side_effect(steps[j]):
            return j
    return None


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def check_age_gate(steps):
    for i, step in enumerate(steps):
        data = _data(step)
        if "age_days" not in data or "window_days" not in data:
            continue
        age, window = data["age_days"], data["window_days"]
        if not (_is_number(age) and _is_number(window)) or age <= window:
            continue
        if _first_side_effect_after(steps, i) is not None:
            return Failure(rule="age_gate", step_index=i, field="age_days")
    return None


def check_unused_field(steps):
    for i, step in enumerate(steps):
        data = _data(step)
        # A step that also carries window_days is the step consuming the
        # field (an eligibility comparison), so the field is not "unused".
        if "window_days" in data:
            continue
        for field in TRACKED_FIELDS:
            if field not in data:
                continue
            j = _first_side_effect_after(steps, i)
            if j is None:
                continue
            if not any(field in _data(steps[k]) for k in range(i + 1, j)):
                return Failure(rule="unused_field", step_index=i, field=field)
    return None


def check_constraint(steps):
    for i, step in enumerate(steps):
        if step.get("step") != "extract_constraint":
            continue
        j = _first_side_effect_after(steps, i)
        if j is None:
            continue
        between = (_data(steps[k]) for k in range(i + 1, j))
        if not any(key in d for d in between for key in OVERRIDE_KEYS):
            return Failure(rule="constraint", step_index=i, field="constraint_value")
    return None
