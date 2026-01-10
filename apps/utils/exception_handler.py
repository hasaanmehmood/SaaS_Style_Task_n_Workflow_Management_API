"""Custom exception handler for better error responses."""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    # Log the exception
    logger.error(f"API Exception: {str(exc)}", exc_info=True)

    if response is not None:
        # Customize the response data
        custom_response = {
            'error': True,
            'status_code': response.status_code,
        }

        # Add error details
        if isinstance(response.data, dict):
            if 'detail' in response.data:
                custom_response['message'] = response.data['detail']
            else:
                custom_response['message'] = 'Validation error'
                custom_response['field_errors'] = response.data
        else:
            custom_response['message'] = str(response.data)

        response.data = custom_response

    return response