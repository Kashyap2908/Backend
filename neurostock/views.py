from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny

from common.responses import success_response


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def health_check(_request):
    return success_response(data={"status": "ok"}, message="Service is healthy")
