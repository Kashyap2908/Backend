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
def list_invoices(request):
    page, page_size = get_pagination_params(request)
    # TODO: inject BillingRepository + BillingService
    return paginated_response(data=[], total=0, page=page, page_size=page_size)


@api_view(["POST"])
@authentication_classes(_DEFAULT_AUTH)
@permission_classes(_DEFAULT_PERM)
def create_invoice(request):
    ctx = request.user_context
    # TODO: inject BillingRepository + BillingService
    return success_response(data={}, message="Invoice created", http_status=201)


@api_view(["GET"])
@authentication_classes(_DEFAULT_AUTH)
@permission_classes(_DEFAULT_PERM)
def get_invoice(request, invoice_id):
    # TODO: inject BillingRepository + BillingService
    return success_response(data={}, message="Invoice retrieved")


@api_view(["PATCH"])
@authentication_classes(_DEFAULT_AUTH)
@permission_classes(_DEFAULT_PERM)
def mark_paid(request, invoice_id):
    ctx = request.user_context
    # TODO: inject BillingRepository + BillingService
    return success_response(message="Invoice marked as paid")
