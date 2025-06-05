from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework import status
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    """
    Manejador de excepciones personalizado para la API.
    Formatea las respuestas de error de manera consistente.
    """
    # Primero, obtener la respuesta estándar
    response = exception_handler(exc, context)
    
    # Si hay una respuesta (es una excepción conocida)
    if response is not None:
        error_data = {
            'error': True,
            'message': str(exc),
            'status_code': response.status_code
        }
        
        # Si hay detalles adicionales, incluirlos
        if hasattr(exc, 'detail'):
            if isinstance(exc.detail, dict):
                error_data['details'] = exc.detail
            else:
                error_data['details'] = {'detail': exc.detail}
        
        response.data = error_data
    
    return response


class BusinessLogicException(APIException):
    """
    Excepción para errores de lógica de negocio.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Ha ocurrido un error en la lógica de negocio.'
    default_code = 'business_logic_error'


class ResourceNotFoundException(APIException):
    """
    Excepción para recursos no encontrados.
    """
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'El recurso solicitado no fue encontrado.'
    default_code = 'resource_not_found'