from django.urls import path
from .views import (
    venta_list, venta_create, venta_detail, venta_edit, venta_anular,
    pago_create, pago_edit, pago_anular,
    reporte_ventas_periodo, reporte_ventas_cliente, reporte_ventas_producto,
    imprimir_factura
)

app_name = 'ventas'

urlpatterns = [
    # Ventas (incluye proformas)
    path('', venta_list, name='venta_list'),
    path('crear/', venta_create, name='venta_create'),
    path('<int:pk>/', venta_detail, name='venta_detail'),
    path('<int:pk>/editar/', venta_edit, name='venta_edit'),
    path('<int:pk>/anular/', venta_anular, name='venta_anular'),
    path('<int:pk>/imprimir/', imprimir_factura, name='imprimir_factura'),
    
    # Pagos
    path('<int:venta_id>/pago/crear/', pago_create, name='pago_create'),
    path('pago/<int:pk>/editar/', pago_edit, name='pago_edit'),
    path('pago/<int:pk>/anular/', pago_anular, name='pago_anular'),
    
    # Reportes
    path('reportes/periodo/', reporte_ventas_periodo, name='reporte_ventas_periodo'),
    path('reportes/cliente/', reporte_ventas_cliente, name='reporte_ventas_cliente'),
    path('reportes/producto/', reporte_ventas_producto, name='reporte_ventas_producto'),
]