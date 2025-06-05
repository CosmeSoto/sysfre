from threading import local
from django.utils import timezone
from django.contrib.auth import logout
from django.shortcuts import redirect
import logging

_usuario_actual = local()
logger = logging.getLogger('sysfree')


class UsuarioActualMiddleware:
    """
    Middleware para almacenar el usuario actual en un thread local.
    Esto permite acceder al usuario actual desde cualquier parte del código.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        _usuario_actual.user = request.user
        response = self.get_response(request)
        return response


def get_usuario_actual():
    """
    Retorna el usuario actual almacenado en el thread local.
    Si no hay usuario autenticado, retorna None.
    """
    try:
        return _usuario_actual.user
    except AttributeError:
        return None


class SessionControlMiddleware:
    """
    Middleware para controlar la duración de las sesiones de usuario.
    Cierra la sesión si ha estado inactivo por más de 30 minutos.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.user.is_authenticated:
            # Verificar última actividad
            last_activity = request.session.get('last_activity')
            now = timezone.now().timestamp()
            
            # Si han pasado más de 30 minutos, invalidar sesión
            if last_activity and now - last_activity > 1800:  # 30 minutos
                logger.info(f"Sesión expirada para el usuario {request.user.email}")
                logout(request)
                return redirect('core:login')
            
            # Actualizar timestamp de última actividad
            request.session['last_activity'] = now
        
        response = self.get_response(request)
        return response


class RequestLoggingMiddleware:
    """
    Middleware para registrar información sobre las solicitudes HTTP.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Registrar la solicitud
        if request.user.is_authenticated:
            user_info = f"Usuario: {request.user.email}"
        else:
            user_info = "Usuario: Anónimo"
            
        logger.info(f"Solicitud: {request.method} {request.path} - {user_info}")
        
        response = self.get_response(request)
        
        # Registrar la respuesta
        logger.info(f"Respuesta: {request.path} - Status: {response.status_code}")
        
        return response