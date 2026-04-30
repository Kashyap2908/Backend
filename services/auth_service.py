import logging
import uuid
from datetime import datetime, timezone

import jwt
from django.conf import settings

from common.exceptions import AuthenticationError, ConflictError, NotFoundError, ValidationError
from common.utils import generate_uuid, validate_email, validate_password_strength
from repositories.user_repository import UserRepository
from repositories.activity_log_repository import ActivityLogRepository

logger = logging.getLogger(__name__)

_user_repo = UserRepository()
_log_repo = ActivityLogRepository()


def _now() -> datetime:
    return datetime.now(tz=timezone.utc)


def _make_access_token(user: dict) -> str:
    payload = {
        "user_id": str(user["id"]),
        "email": user["email"],
        "branch_id": str(user["branch_id"]) if user.get("branch_id") else None,
        "role": user.get("role"),
        "exp": _now() + settings.JWT_ACCESS_TOKEN_EXPIRY,
        "iat": _now(),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")


def _make_refresh_token() -> str:
    return str(uuid.uuid4())


class AuthService:
    def register(self, email: str, password: str) -> dict:
        email = validate_email(email)
        validate_password_strength(password)

        if _user_repo.find_by_email(email):
            raise ConflictError("An account with this email already exists")

        user = _user_repo.create_user(email=email, password=password)

        access_token = _make_access_token(user)
        refresh_token = _make_refresh_token()
        expires_at = _now() + settings.JWT_REFRESH_TOKEN_EXPIRY
        _user_repo.store_refresh_token(
            user_id=str(user["id"]),
            token=refresh_token,
            branch_id=str(user["branch_id"]) if user.get("branch_id") else None,
            expires_at=expires_at,
        )

        _log_repo.log(
            action="register",
            user_id=str(user["id"]),
            branch_id=str(user["branch_id"]) if user.get("branch_id") else None,
        )

        logger.info("New user registered: %s", user["email"])

        return {
            "access": access_token,
            "refresh": refresh_token,
            "user": {
                "id": str(user["id"]),
                "email": user["email"],
                "role": user.get("role"),
                "branch_id": str(user["branch_id"]) if user.get("branch_id") else None,
            },
        }

    def login(self, email: str, password: str, ip_address: str | None = None) -> dict:
        email = validate_email(email)

        user = _user_repo.find_by_email(email)
        if not user:
            # Uniform message to prevent user enumeration
            _log_repo.log(action="login_failed", details={"reason": "user_not_found", "email": email}, ip_address=ip_address)
            raise AuthenticationError("Invalid email or password")

        is_valid = _user_repo.verify_password(password, user["password_hash"])
        if not is_valid:
            _log_repo.log(
                action="login_failed",
                user_id=str(user["id"]),
                branch_id=str(user["branch_id"]) if user.get("branch_id") else None,
                details={"reason": "wrong_password"},
                ip_address=ip_address,
            )
            raise AuthenticationError("Invalid email or password")

        access_token = _make_access_token(user)

        refresh_token = _make_refresh_token()
        expires_at = _now() + settings.JWT_REFRESH_TOKEN_EXPIRY
        _user_repo.store_refresh_token(
            user_id=str(user["id"]),
            token=refresh_token,
            branch_id=str(user["branch_id"]) if user.get("branch_id") else None,
            expires_at=expires_at,
        )

        _log_repo.log(
            action="login_success",
            user_id=str(user["id"]),
            branch_id=str(user["branch_id"]) if user.get("branch_id") else None,
            ip_address=ip_address,
        )

        logger.info("User %s logged in from %s", user["email"], ip_address)

        return {
            "access": access_token,
            "refresh": refresh_token,
            "user": {
                "id": str(user["id"]),
                "email": user["email"],
                "role": user.get("role"),
                "branch_id": str(user["branch_id"]) if user.get("branch_id") else None,
            },
        }

    def refresh_access_token(self, refresh_token: str) -> dict:
        if not refresh_token:
            raise ValidationError("Refresh token is required")

        record = _user_repo.find_refresh_token(refresh_token)
        if not record:
            raise AuthenticationError("Invalid refresh token")

        if record["is_revoked"]:
            raise AuthenticationError("Refresh token has been revoked")

        expires_at = record["expires_at"]
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at)
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if _now() > expires_at:
            raise AuthenticationError("Refresh token has expired. Please log in again")

        user = {
            "id": record["user_id"],
            "email": record["email"],
            "branch_id": record.get("branch_id"),
            "role": record.get("role"),
        }
        new_access_token = _make_access_token(user)
        return {"access": new_access_token}

    def logout(self, refresh_token: str, user_id: str | None = None) -> None:
        if refresh_token:
            _user_repo.revoke_refresh_token(refresh_token)
        if user_id:
            _log_repo.log(action="logout", user_id=user_id)

    def request_password_reset(self, email: str) -> str:
        email = validate_email(email)

        user = _user_repo.find_by_email(email)
        # Return success even if email not found (prevent enumeration)
        if not user:
            logger.info("Password reset requested for unknown email: %s", email)
            return generate_uuid()

        token = generate_uuid()
        expires_at = _now() + settings.PASSWORD_RESET_TOKEN_EXPIRY

        _user_repo.create_reset_token(
            user_id=str(user["id"]),
            token=token,
            expires_at=expires_at,
        )

        _log_repo.log(
            action="password_reset_requested",
            user_id=str(user["id"]),
        )

        logger.info("Password reset token generated for user %s", user["id"])
        return token

    def reset_password(self, token: str, new_password: str) -> None:
        validate_password_strength(new_password)

        record = _user_repo.find_reset_token(token)
        if not record:
            raise ValidationError("Invalid or expired reset token")

        if record["used"]:
            raise ValidationError("This reset token has already been used")

        expires_at = record["expires_at"]
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at)
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if _now() > expires_at:
            raise ValidationError("Reset token has expired. Please request a new one")

        _user_repo.update_password(str(record["user_id"]), new_password)
        _user_repo.mark_reset_token_used(token)

        _log_repo.log(
            action="password_reset_completed",
            user_id=str(record["user_id"]),
        )

        logger.info("Password reset completed for user %s", record["user_id"])
