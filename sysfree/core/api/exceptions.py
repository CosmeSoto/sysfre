from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Custom exception handler for API.
    """
    response = exception_handler(exc, context)
    
    if response is not None:
        # Add more context to the error response
        if isinstance(exc, APIException):
            if hasattr(exc, 'detail') and isinstance(exc.detail, dict):
                response.data = {
                    'error': True,
                    'message': 'Validation error',
                    'details': exc.detail
                }
            else:
                response.data = {
                    'error': True,
                    'message': str(exc),
                    'details': getattr(exc, 'detail', None)
                }
    
    return response


class BusinessLogicException(APIException):
    """
    Exception for business logic errors.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'A business logic error occurred.'
    default_code = 'business_logic_error'


class ResourceNotFoundException(APIException):
    """
    Exception for resource not found errors.
    """
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'The requested resource was not found.'
    default_code = 'resource_not_found'


class PermissionDeniedException(APIException):
    """
    Exception for permission denied errors.
    """
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'You do not have permission to perform this action.'
    default_code = 'permission_denied'