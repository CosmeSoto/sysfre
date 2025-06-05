from django.urls import path
from .views import (
    reparacion_list, reparacion_create, reparacion_detail, reparacion_edit, reparacion_cambiar_estado,
    seguimiento_create,
    repuesto_create, repuesto_edit, repuesto_delete,
    reparacion_facturar, reparacion_proforma,
    reporte_reparaciones_periodo, reporte_reparaciones_tecnico, reporte_reparaciones_estado,
    imprimir_orden, imprimir_recibo
)

app_name = 'reparaciones'

urlpatterns = [
    # Reparaciones
    path('', reparacion_list, name='reparacion_list'),
    path('crear/', reparacion_create, name='reparacion_create'),
    path('<int:pk>/', reparacion_detail, name='reparacion_detail'),
    path('<int:pk>/editar/', reparacion_edit, name='reparacion_edit'),
    path('<int:pk>/cambiar-estado/', reparacion_cambiar_estado, name='reparacion_cambiar_estado'),
    
    # Seguimientos
    path('<int:reparacion_id>/seguimiento/crear/', seguimiento_create, name='seguimiento_create'),
    
    # Repuestos
    path('<int:reparacion_id>/repuesto/agregar/', repuesto_create, name='repuesto_create'),
    path('repuesto/<int:pk>/editar/', repuesto_edit, name='repuesto_edit'),
    path('repuesto/<int:pk>/eliminar/', repuesto_delete, name='repuesto_delete'),
    
    # Facturación y Proformas
    path('<int:pk>/facturar/', reparacion_facturar, name='reparacion_facturar'),
    path('<int:pk>/proforma/', reparacion_proforma, name='reparacion_proforma'),
    
    # Reportes
    path('reportes/reparaciones-por-periodo/', reporte_reparaciones_periodo, name='reporte_reparaciones_periodo'),
    path('reportes/reparaciones-por-tecnico/', reporte_reparaciones_tecnico, name='reporte_reparaciones_tecnico'),
    path('reportes/reparaciones-por-estado/', reporte_reparaciones_estado, name='reporte_reparaciones_estado'),
    
    # Impresión
    path('<int:pk>/imprimir-orden/', imprimir_orden, name='imprimir_orden'),
    path('<int:pk>/imprimir-recibo/', imprimir_recibo, name='imprimir_recibo'),
]