import logging
from functools import wraps

import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import BasePermission

from common.exceptions import AuthenticationError, AuthorizationError

logger = logging.getLogger(__name__)


class JWTAuthentication(BaseAuthentication):
    """
    DRF authentication backend that validates Bearer JWTs and populates
    request.user_context with {user_id, branch_id, role, email}.
    """

    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split(" ", 1)[1].strip()
        if not token:
            raise AuthenticationError("Bearer token is empty")

        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=["HS256"],
            )
        except jwt.ExpiredSignatureError:
            logger.warning("Expired JWT token presented")
            raise AuthenticationError("Token has expired. Please log in again")
        except jwt.InvalidTokenError as exc:
            logger.warning("Invalid JWT token: %s", exc)
            raise AuthenticationError("Invalid token")

        user_context = {
            "user_id": payload.get("user_id"),
            "branch_id": payload.get("branch_id"),
            "role": payload.get("role"),
            "email": payload.get("email"),
        }
        request.user_context = user_context
        # Return (user, auth) — user is the raw payload dict (no Django User model)
        return (payload, token)

    def authenticate_header(self, request):
        return "Bearer"


class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return (
            hasattr(request, "user_context")
            and request.user_context.get("user_id") is not None
        )


class IsAdminRole(BasePermission):
    """Allow only users whose token role is 'admin'."""

    def has_permission(self, request, view):
        ctx = getattr(request, "user_context", {})
        return ctx.get("role") == "admin"


def require_roles(*roles):
    """Decorator factory: restrict a view to specific roles."""

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            ctx = getattr(request, "user_context", {})
            if ctx.get("role") not in roles:
                raise AuthorizationError(
                    f"This action requires one of the following roles: {', '.join(roles)}"
                )
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
