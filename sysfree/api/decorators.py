from functools import wraps
from rest_framework.response import Response
from rest_framework import status
import logging
import time

logger = logging.getLogger('sysfree')


def log_api_call(func):
    """
    Decorador para registrar llamadas a la API.
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        start_time = time.time()
        
        # Registrar la llamada
        logger.info(f"API Call: {request.method} {request.path} by {request.user}")
        
        # Ejecutar la función
        response = func(request, *args, **kwargs)
        
        # Registrar el tiempo de respuesta
        elapsed_time = time.time() - start_time
        logger.info(f"API Response: {request.path} - Status: {response.status_code} - Time: {elapsed_time:.3f}s")
        
        return response
    return wrapper


def require_params(*required_params):
    """
    Decorador para verificar que los parámetros requeridos estén presentes.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            missing_params = [param for param in required_params if param not in request.query_params]
            
            if missing_params:
                return Response(
                    {
                        'error': True,
                        'message': f"Faltan parámetros requeridos: {', '.join(missing_params)}",
                        'status_code': status.HTTP_400_BAD_REQUEST
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return func(request, *args, **kwargs)
        return wrapper
    return decorator