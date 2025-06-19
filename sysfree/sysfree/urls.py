"""
Configuración de URLs para el proyecto sysfree.

Define las rutas principales para las aplicaciones del sistema, incluyendo
el panel de administración, APIs, módulos de negocio (clientes, inventario, etc.),
y el endpoint de métricas de Prometheus. Los archivos estáticos y media se sirven
solo en modo DEBUG para desarrollo.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .metrics import metrics_view
from django.contrib.auth.decorators import login_required

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # APIs
    path('api/', include('api.urls')),
    
    # Aplicaciones de negocio
    path('', include('core.urls', namespace='core')),
    path('clientes/', include('clientes.urls', namespace='clientes')),
    path('inventario/', include('inventario.urls', namespace='inventario')),
    path('ventas/', include('ventas.urls', namespace='ventas')),
    path('fiscal/', include('fiscal.urls', namespace='fiscal')),
    path('reparaciones/', include('reparaciones.urls', namespace='reparaciones')),
    path('reportes/', include('reportes.urls', namespace='reportes')),
    path('tienda/', include('ecommerce.urls', namespace='ecommerce')),
    
    # Monitoreo - Protegido por login_required
    path('metrics/', login_required(metrics_view), name='prometheus-metrics'),
]

# Servir archivos estáticos y media solo en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)