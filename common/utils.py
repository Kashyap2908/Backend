import uuid
import re
from typing import Any

from common.exceptions import ValidationError


def generate_uuid() -> str:
    return str(uuid.uuid4())


def validate_required_fields(data: dict, fields: list[str]) -> None:
    """Raise ValidationError listing every missing or blank required field."""
    missing = [f for f in fields if not data.get(f)]
    if missing:
        raise ValidationError(
            message=f"Missing required fields: {', '.join(missing)}",
            details={"missing_fields": missing},
        )


def validate_email(email: str) -> str:
    """Return the lowercased email or raise ValidationError."""
    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email or ""):
        raise ValidationError(message="Invalid email address format")
    return email.lower().strip()


def validate_password_strength(password: str) -> None:
    if len(password) < 8:
        raise ValidationError(message="Password must be at least 8 characters long")


def get_client_ip(request) -> str | None:
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
        return ip or None
    ip = request.META.get("REMOTE_ADDR", "")
    return ip or None


def get_pagination_params(request) -> tuple[int, int]:
    """Return (page, page_size) validated from query params."""
    try:
        page = max(1, int(request.query_params.get("page", 1)))
        page_size = min(100, max(1, int(request.query_params.get("page_size", 20))))
    except (ValueError, TypeError):
        raise ValidationError(message="page and page_size must be positive integers")
    return page, page_size


def build_pagination_sql(page: int, page_size: int) -> tuple[str, list[Any]]:
    """Return LIMIT/OFFSET SQL fragment and params for the given page."""
    offset = (page - 1) * page_size
    return "LIMIT %s OFFSET %s", [page_size, offset]
