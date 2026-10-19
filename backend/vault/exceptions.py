import logging

from django.db import DatabaseError
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


class StorageUnavailable(APIException):
    status_code = 502
    default_detail = "File storage is unavailable right now. Please try again."
    default_code = "storage_unavailable"


def api_exception_handler(exc, context):
    if isinstance(exc, DatabaseError):
        logger.exception("Database error")
        return Response({"detail": "The database is temporarily unavailable. Please try again."}, status=503)
    return exception_handler(exc, context)
