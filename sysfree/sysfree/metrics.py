from django.http import HttpResponse, HttpResponseForbidden
from django.conf import settings
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

def metrics_view(request):
    """
    Vista para exponer métricas de Prometheus en el endpoint /metrics/.
    Solo accesible desde direcciones IP confiables (por defecto, localhost).
    Retorna métricas en formato Prometheus con el tipo de contenido adecuado.
    """
    # Verifica si la solicitud proviene de una IP permitida
    client_ip = request.META.get('REMOTE_ADDR')
    allowed_ips = getattr(settings, 'PROMETHEUS_ALLOWED_IPS', ['127.0.0.1', '::1'])
    if client_ip not in allowed_ips:
        return HttpResponseForbidden("Access to metrics is restricted")

    try:
        # Genera y retorna las métricas de Prometheus
        return HttpResponse(
            generate_latest(),
            content_type=CONTENT_TYPE_LATEST
        )
    except Exception as e:
        # Registra el error y retorna un error 500
        from logging import getLogger
        logger = getLogger('sysfree')
        logger.error(f"Error generating Prometheus metrics: {str(e)}")
        return HttpResponse("Internal Server Error", status=500)