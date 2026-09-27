"""
Why this file exists:
"Input validation on all write operations" is a hard
requirement in the task guide. Rather than repeating the same
checks in every route, we write small, reusable validator
functions here once, and call them from routes.
"""

import re
from app.errors import ApiError

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
VALID_TASK_STATUSES = {"todo", "in-progress", "done"}
VALID_PRIORITIES = {"low", "medium", "high"}


def require_fields(data, fields):
    """Raises a 400 error if any required field is missing or empty."""
    if not isinstance(data, dict):
        raise ApiError("Request body must be a JSON object.", 400)

    missing = [f for f in fields if not str(data.get(f, "")).strip()]
    if missing:
        raise ApiError(
            "Missing required field(s).",
            400,
            details={"missing_fields": missing},
        )


def validate_email(email):
    if not EMAIL_PATTERN.match(email):
        raise ApiError("Invalid email format.", 400, details={"field": "email"})


def validate_choice(value, allowed, field_name):
    if value not in allowed:
        raise ApiError(
            f"Invalid value for '{field_name}'.",
            400,
            details={"field": field_name, "allowed": sorted(allowed)},
        )
