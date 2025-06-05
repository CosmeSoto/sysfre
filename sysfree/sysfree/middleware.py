import time
import logging
from django.utils.deprecation import MiddlewareMixin

access_logger = logging.getLogger('access')

class RequestLoggingMiddleware(MiddlewareMixin):
    """Middleware para registrar información detallada sobre todas las solicitudes HTTP."""
    
    def process_request(self, request):
        request.start_time = time.time()
    
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration_ms = (time.time() - request.start_time) * 1000
            user = request.user.username if request.user.is_authenticated else 'Anonymous'
            access_logger.info(
                '"%(method)s %(path)s HTTP/1.1" %(status_code)s %(content_length)s',
                extra={
                    'user': user,
                    'method': request.method,
                    'path': request.get_full_path(),
                    'status_code': response.status_code,
                    'content_length': response.get('Content-Length', 0),
                    'response_time_ms': duration_ms,
                }
            )
        return response

class PrometheusMiddleware(MiddlewareMixin):
    """Middleware para recopilar métricas para Prometheus."""
    
    def process_request(self, request):
        request.start_time = time.time()
    
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
        return response

class SecurityMiddleware(MiddlewareMixin):
    """Middleware para añadir cabeceras de seguridad."""
    
    def process_response(self, request, response):
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' cdn.jsdelivr.net; "
            "img-src 'self' data:; "
            "font-src 'self' cdn.jsdelivr.net;"
        )
        return response