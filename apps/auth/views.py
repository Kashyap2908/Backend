import logging

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny

from common.auth import JWTAuthentication, IsAuthenticated
from common.responses import success_response
from common.utils import validate_required_fields, get_client_ip
from services.auth_service import AuthService

logger = logging.getLogger(__name__)

_auth_service = AuthService()


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def register(request):
    validate_required_fields(request.data, ["email", "password"])

    result = _auth_service.register(
        email=request.data["email"],
        password=request.data["password"],
    )
    return success_response(data=result, message="Account created successfully", http_status=201)


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def login(request):
    validate_required_fields(request.data, ["email", "password"])

    result = _auth_service.login(
        email=request.data["email"],
        password=request.data["password"],
        ip_address=get_client_ip(request),
    )
    return success_response(data=result, message="Login successful")


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def refresh_token(request):
    validate_required_fields(request.data, ["refresh"])

    result = _auth_service.refresh_access_token(request.data["refresh"])
    return success_response(data=result, message="Token refreshed")


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    _auth_service.logout(
        refresh_token=request.data.get("refresh", ""),
        user_id=request.user_context.get("user_id"),
    )
    return success_response(message="Logged out successfully")


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def request_reset(request):
    validate_required_fields(request.data, ["email"])

    # Token is returned directly here; in production this should be emailed
    token = _auth_service.request_password_reset(email=request.data["email"])
    return success_response(
        data={"token": token},
        message="If that email is registered, a reset token has been generated",
    )


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def reset_password(request):
    validate_required_fields(request.data, ["token", "new_password"])

    _auth_service.reset_password(
        token=request.data["token"],
        new_password=request.data["new_password"],
    )
    return success_response(message="Password reset successfully")
