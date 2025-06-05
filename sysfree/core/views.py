from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import logging
from .log_utils import log_function_call, log_security_event

# Configurar logger
logger = logging.getLogger('sysfree')

@login_required
@log_function_call
def dashboard(request):
    """Vista para el dashboard principal."""
    logger.info(f"Usuario {request.user.email} accedió al dashboard")
    log_security_event('acceso_dashboard', user=request.user.email)
    return render(request, 'core/dashboard.html')