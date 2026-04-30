import logging

from rest_framework.decorators import api_view, authentication_classes, permission_classes

from common.auth import JWTAuthentication, IsAuthenticated
from common.responses import success_response, paginated_response
from common.utils import get_pagination_params
from repositories.activity_log_repository import ActivityLogRepository

logger = logging.getLogger(__name__)

_DEFAULT_AUTH = [JWTAuthentication]
_DEFAULT_PERM = [IsAuthenticated]

_log_repo = ActivityLogRepository()


@api_view(["GET"])
@authentication_classes(_DEFAULT_AUTH)
@permission_classes(_DEFAULT_PERM)
def dashboard_summary(request):
    """GET /api/dashboard/ — key KPIs for the branch dashboard."""
    ctx = request.user_context
    # TODO: inject AnalyticsRepository
    return success_response(
        data={
            "branch_id": ctx.get("branch_id"),
            "total_sales": 0,
            "total_transactions": 0,
            "low_stock_items": 0,
        },
        message="Dashboard data retrieved",
    )


@api_view(["GET"])
@authentication_classes(_DEFAULT_AUTH)
@permission_classes(_DEFAULT_PERM)
def sales_report(request):
    ctx = request.user_context
    # TODO: inject AnalyticsRepository
    return success_response(data={}, message="Sales report retrieved")


@api_view(["GET"])
@authentication_classes(_DEFAULT_AUTH)
@permission_classes(_DEFAULT_PERM)
def stock_report(request):
    ctx = request.user_context
    # TODO: inject AnalyticsRepository
    return success_response(data={}, message="Stock report retrieved")


@api_view(["GET"])
@authentication_classes(_DEFAULT_AUTH)
@permission_classes(_DEFAULT_PERM)
def activity_logs(request):
    page, page_size = get_pagination_params(request)
    ctx = request.user_context

    branch_id = ctx.get("branch_id")
    total = _log_repo.count_logs(branch_id=branch_id)
    logs = _log_repo.get_logs(
        branch_id=branch_id,
        limit=page_size,
        offset=(page - 1) * page_size,
    )
    return paginated_response(data=logs, total=total, page=page, page_size=page_size)
