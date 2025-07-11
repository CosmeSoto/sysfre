from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from ..services.configuracion_service import ConfiguracionService
from ..log_utils import log_function_call, log_security_event
from ..models import Empresa, Sucursal
import logging

# Configurar logger
logger = logging.getLogger('sysfree')

@login_required
@log_function_call
def dashboard_view(request):
    """Vista para el dashboard principal del sistema."""
    
    # Registrar el acceso al dashboard
    logger.info(f"Usuario {request.user.email} accedió al dashboard")
    log_security_event('acceso_dashboard', user=request.user.email)

    # Obtener el nombre del usuario para un mensaje personalizado
    nombre_usuario = request.user.nombres or request.user.email.split('@')[0]

    # Obtener información de la empresa
    empresa = Empresa.objects.first()
    sistema_nombre = empresa.nombre if empresa else 'SysFree'
    sistema_version = '1.0.0'  # Valor fijo

    # Obtener el total de sucursales
    total_sucursales = Sucursal.objects.count()

    # Crear el contexto para la plantilla
    context = {
        'title': _('Dashboard'),
        'sistema_nombre': sistema_nombre,
        'sistema_version': sistema_version,
        'mensaje_bienvenida': f'¡Bienvenido, {nombre_usuario}!',
        'empresa': empresa,
        'total_sucursales': total_sucursales,
    }
    
    return render(request, 'core/dashboard/index.html', context)