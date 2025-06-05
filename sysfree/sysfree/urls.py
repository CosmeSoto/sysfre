"""
URL Configuration for sysfree project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('', include('core.urls')), # Keep core URLs at the root
    path('clientes/', include('clientes.urls', namespace='clientes')),
    path('inventario/', include('inventario.urls', namespace='inventario')),
    path('ventas/', include('ventas.urls', namespace='ventas')),
    path('fiscal/', include('fiscal.urls', namespace='fiscal')),
    path('reparaciones/', include('reparaciones.urls', namespace='reparaciones')),
    path('reportes/', include('reportes.urls', namespace='reportes')),
    path('tienda/', include('ecommerce.urls', namespace='ecommerce')), # Using 'tienda' as prefix
]

# Servir archivos estáticos y media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)