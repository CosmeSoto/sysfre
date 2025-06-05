from django.urls import path
from .views import (
    dashboard, reporte_ventas, reporte_inventario, reporte_reparaciones
)

app_name = 'reportes'

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('ventas/', reporte_ventas, name='ventas'),
    path('inventario/', reporte_inventario, name='inventario'),
    path('reparaciones/', reporte_reparaciones, name='reparaciones'),
]