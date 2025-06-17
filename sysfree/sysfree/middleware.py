import time
import logging
from django.utils.deprecation import MiddlewareMixin
from django.urls import resolve, Resolver404
from .monitoring import REQUEST_COUNT, REQUEST_LATENCY

# Logger para registrar solicitudes HTTP
access_logger = logging.getLogger('access')

class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware para registrar información detallada de solicitudes HTTP en logs.
    Registra método, ruta, código de estado, tiempo de respuesta y usuario.
    """
    
    def process_request(self, request):
        """Almacena el tiempo de inicio de la solicitud."""
        request.start_time = time.time()
    
    def process_response(self, request, response):
        """
        Registra la solicitud en el logger 'access' con detalles relevantes.
        Calcula el tiempo de respuesta en milisegundos.
        """
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
    """
    Middleware para recopilar métricas de Prometheus sobre solicitudes HTTP.
    Registra el conteo de solicitudes (REQUEST_COUNT) y la latencia (REQUEST_LATENCY)
    con etiquetas para método HTTP, patrón de endpoint y código de estado.
    """
    
    def process_request(self, request):
        """Registra el tiempo de inicio para calcular la latencia."""
        request.prometheus_start_time = time.time()

    def process_response(self, request, response):
        """
        Registra métricas de Prometheus: conteo de solicitudes y latencia.
        Usa el patrón de ruta resuelto para agrupar URLs dinámicas, mejorando
        la cardinalidad de las métricas y evitando explosión de etiquetas.
        """
        if hasattr(request, 'prometheus_start_time'):
            duration = time.time() - request.prometheus_start_time

            # Determina el patrón de endpoint para métricas consistentes
            endpoint_pattern = request.path_info
            try:
                resolved_match = resolve(request.path_info)
                # Usa el patrón de ruta (route) para URLs dinámicas (ej. /api/users/<id>/)
                if resolved_match and hasattr(resolved_match, 'route'):
                    endpoint_pattern = resolved_match.route or request.path_info
            except Resolver404:
                # Si la ruta no se resuelve, usa la ruta original
                pass

            # Registra la latencia con etiquetas de método y endpoint
            REQUEST_LATENCY.labels(
                method=request.method,
                endpoint=endpoint_pattern
            ).observe(duration)

            # Incrementa el contador de solicitudes con etiquetas de método, endpoint y código de estado
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=endpoint_pattern,
                status_code=response.status_code
            ).inc()

        return response

class SecurityMiddleware(MiddlewareMixin):
    """
    Middleware para añadir cabeceras de seguridad HTTP y configurar Content Security Policy (CSP).
    Mejora la protección contra ataques como XSS, clickjacking y MIME-type sniffing.
    """
    
    def process_response(self, request, response):
        """
        Añade cabeceras de seguridad y configura CSP para restringir recursos permitidos.
        Nota sobre CSP: Se incluye 'unsafe-inline' temporalmente para compatibilidad con
        scripts/estilos inline, pero debe eliminarse en el futuro para mayor seguridad,
        reemplazando con nonces o hashes. También se permite cdn.jsdelivr.net, pero
        debe revisarse la confianza en este CDN y considerar alternativas como un CDN propio.
        """
        # Evita que los navegadores interpreten archivos con tipos MIME incorrectos
        response['X-Content-Type-Options'] = 'nosniff'
        
        # Cabecera obsoleta, pero mantenida por compatibilidad con navegadores antiguos
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Controla la información enviada en el encabezado Referer
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Configuración de Content Security Policy (CSP)
        # - 'default-src 'self'': Solo permite recursos del mismo origen por defecto
        # - 'script-src': Permite scripts del mismo origen, inline (temporal) y cdn.jsdelivr.net
        # - 'style-src': Similar a script-src, permite estilos inline (temporal)
        # - 'img-src': Permite imágenes del mismo origen y datos URI (data:)
        # - 'font-src': Permite fuentes del mismo origen y cdn.jsdelivr.net
        # TODO: Eliminar 'unsafe-inline' y usar nonces/hashes para scripts y estilos
        # TODO: Revisar la necesidad de cdn.jsdelivr.net; considerar un CDN propio
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' cdn.jsdelivr.net; "
            "img-src 'self' data:; "
            "font-src 'self' cdn.jsdelivr.net;"
        )
        
        return response