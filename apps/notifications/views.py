import logging

from rest_framework.decorators import api_view, authentication_classes, permission_classes

from common.auth import JWTAuthentication, IsAuthenticated
from common.responses import success_response, paginated_response
from common.utils import get_pagination_params

logger = logging.getLogger(__name__)

_DEFAULT_AUTH = [JWTAuthentication]
_DEFAULT_PERM = [IsAuthenticated]


@api_view(["GET"])
@authentication_classes(_DEFAULT_AUTH)
@permission_classes(_DEFAULT_PERM)
def list_notifications(request):
    page, page_size = get_pagination_params(request)
    ctx = request.user_context
    # TODO: inject NotificationRepository
    return paginated_response(data=[], total=0, page=page, page_size=page_size)


@api_view(["PATCH"])
@authentication_classes(_DEFAULT_AUTH)
@permission_classes(_DEFAULT_PERM)
def mark_read(request, notification_id):
    ctx = request.user_context
    # TODO: inject NotificationRepository
    return success_response(message="Notification marked as read")


@api_view(["PATCH"])
@authentication_classes(_DEFAULT_AUTH)
@permission_classes(_DEFAULT_PERM)
def mark_all_read(request):
    ctx = request.user_context
    # TODO: inject NotificationRepository
    return success_response(message="All notifications marked as read")
