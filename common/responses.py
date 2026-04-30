import math
from rest_framework.response import Response
from rest_framework import status


def success_response(data=None, message="Success", http_status=status.HTTP_200_OK):
    return Response(
        {
            "success": True,
            "message": message,
            "data": data,
            "error": None,
        },
        status=http_status,
    )


def created_response(data=None, message="Resource created successfully"):
    return success_response(data=data, message=message, http_status=status.HTTP_201_CREATED)


def no_content_response(message="Operation successful"):
    return Response(
        {
            "success": True,
            "message": message,
            "data": None,
            "error": None,
        },
        status=status.HTTP_200_OK,
    )


def error_response(
    message,
    error_code="ERROR",
    details=None,
    http_status=status.HTTP_400_BAD_REQUEST,
):
    return Response(
        {
            "success": False,
            "message": message,
            "data": None,
            "error": {
                "code": error_code,
                "details": details,
            },
        },
        status=http_status,
    )


def paginated_response(data, total, page, page_size, message="Success"):
    total_pages = math.ceil(total / page_size) if page_size > 0 else 0
    return Response(
        {
            "success": True,
            "message": message,
            "data": data,
            "error": None,
            "pagination": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1,
            },
        },
        status=status.HTTP_200_OK,
    )
