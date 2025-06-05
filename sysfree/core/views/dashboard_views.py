from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from ..services.configuracion_service import ConfiguracionService


@login_required
def dashboard_view(request):
    """Vista para el dashboard principal del sistema."""
    
    # Obtener configuraciones del sistema
    sistema_nombre = ConfiguracionService.get_valor('sistema.nombre', 'SysFree')
    sistema_version = ConfiguracionService.get_valor('sistema.version', '1.0.0')
    
    context = {
        'title': _('Dashboard'),
        'sistema_nombre': sistema_nombre,
        'sistema_version': sistema_version,
    }
    
    return render(request, 'core/dashboard/index.html', context)