from rest_framework.exceptions import APIException, NotFound, ParseError, ValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import status


class ApiWrongObjectState(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("Object is not in the correct state.")
    default_code = "wrong_state"


class RpcTimeout(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = _("Some RPC's failed.")
    default_code = "error"
