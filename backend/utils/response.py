from rest_framework.response import Response
from rest_framework import status
from typing import Any


def api_response(data=None, message="", status_code=status.HTTP_200_OK):
    return Response(
        {"data": data, "message": message},
        status=status_code,
    )


def api_error(message: Any, status_code=status.HTTP_400_BAD_REQUEST, data=None):
    return Response(
        {"errors": data, "message": message},
        status=status_code,
    )