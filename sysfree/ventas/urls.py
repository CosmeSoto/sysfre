from django.urls import path
from .views import (
    venta_list, venta_create, venta_detail, venta_edit, venta_anular,
    pago_create, pago_edit, pago_anular,
    proforma_list, proforma_create, proforma_detail, proforma_edit, proforma_convertir,
    reporte_ventas_periodo, reporte_ventas_cliente, reporte_ventas_producto,
    imprimir_factura, imprimir_proforma
)

app_name = 'ventas'

urlpatterns = [
    # Ventas
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
    
    # Proformas
    path('proformas/', proforma_list, name='proforma_list'),
    path('proformas/crear/', proforma_create, name='proforma_create'),
    path('proformas/<int:pk>/', proforma_detail, name='proforma_detail'),
    path('proformas/<int:pk>/editar/', proforma_edit, name='proforma_edit'),
    path('proformas/<int:pk>/convertir/', proforma_convertir, name='proforma_convertir'),
    path('proformas/<int:pk>/imprimir/', imprimir_proforma, name='imprimir_proforma'),
    
    # Reportes
    path('reportes/periodo/', reporte_ventas_periodo, name='reporte_ventas_periodo'),
    path('reportes/cliente/', reporte_ventas_cliente, name='reporte_ventas_cliente'),
    path('reportes/producto/', reporte_ventas_producto, name='reporte_ventas_producto'),
]