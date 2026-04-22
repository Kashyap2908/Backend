from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
@renderer_classes([JSONRenderer])
def health_check(_request):
    return Response(
        {"status": "ok"},
        status=status.HTTP_200_OK,
    )
