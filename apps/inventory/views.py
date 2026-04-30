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
def list_products(request):
    """GET /api/products/ — paginated product list filtered by branch."""
    page, page_size = get_pagination_params(request)
    ctx = request.user_context

    # TODO: inject ProductRepository + ProductService
    return paginated_response(data=[], total=0, page=page, page_size=page_size)


@api_view(["GET"])
@authentication_classes(_DEFAULT_AUTH)
@permission_classes(_DEFAULT_PERM)
def get_product(request, product_id):
    """GET /api/products/<uuid>/ — single product detail."""
    ctx = request.user_context
    # TODO: inject ProductRepository + ProductService
    return success_response(data={}, message="Product retrieved")


@api_view(["POST"])
@authentication_classes(_DEFAULT_AUTH)
@permission_classes(_DEFAULT_PERM)
def create_product(request):
    """POST /api/products/create/ — create a new product."""
    ctx = request.user_context
    # TODO: inject ProductRepository + ProductService
    return success_response(data={}, message="Product created", http_status=201)


@api_view(["PATCH"])
@authentication_classes(_DEFAULT_AUTH)
@permission_classes(_DEFAULT_PERM)
def update_product(request, product_id):
    """PATCH /api/products/<uuid>/update/ — partial update."""
    ctx = request.user_context
    # TODO: inject ProductRepository + ProductService
    return success_response(data={}, message="Product updated")


@api_view(["DELETE"])
@authentication_classes(_DEFAULT_AUTH)
@permission_classes(_DEFAULT_PERM)
def delete_product(request, product_id):
    """DELETE /api/products/<uuid>/delete/"""
    ctx = request.user_context
    # TODO: inject ProductRepository + ProductService
    return success_response(message="Product deleted")


@api_view(["GET"])
@authentication_classes(_DEFAULT_AUTH)
@permission_classes(_DEFAULT_PERM)
def stock_summary(request):
    """GET /api/products/stock/ — low-stock and total stock summary."""
    ctx = request.user_context
    # TODO: inject StockRepository
    return success_response(data={}, message="Stock summary retrieved")
