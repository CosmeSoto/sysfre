from django.urls import path
from .views import (
    asiento_list, asiento_create, asiento_detail, asiento_validar, asiento_anular,
    cuenta_list, cuenta_create, cuenta_edit,
    periodo_list, periodo_create, periodo_edit, periodo_cerrar,
    impuesto_list, impuesto_create, impuesto_edit,
    comprobante_list, comprobante_create, comprobante_detail, comprobante_emitir, comprobante_anular,
    reporte_libro_diario, reporte_libro_mayor, reporte_balance_general, reporte_estado_resultados
)

app_name = 'fiscal'

urlpatterns = [
    # Contabilidad
    path('asientos/', asiento_list, name='asiento_list'),
    path('asientos/crear/', asiento_create, name='asiento_create'),
    path('asientos/<int:pk>/', asiento_detail, name='asiento_detail'),
    path('asientos/<int:pk>/validar/', asiento_validar, name='asiento_validar'),
    path('asientos/<int:pk>/anular/', asiento_anular, name='asiento_anular'),
    
    # Cuentas contables
    path('cuentas/', cuenta_list, name='cuenta_list'),
    path('cuentas/crear/', cuenta_create, name='cuenta_create'),
    path('cuentas/<int:pk>/editar/', cuenta_edit, name='cuenta_edit'),
    
    # Periodos fiscales
    path('periodos/', periodo_list, name='periodo_list'),
    path('periodos/crear/', periodo_create, name='periodo_create'),
    path('periodos/<int:pk>/editar/', periodo_edit, name='periodo_edit'),
    path('periodos/<int:pk>/cerrar/', periodo_cerrar, name='periodo_cerrar'),
    
    # Impuestos
    path('impuestos/', impuesto_list, name='impuesto_list'),
    path('impuestos/crear/', impuesto_create, name='impuesto_create'),
    path('impuestos/<int:pk>/editar/', impuesto_edit, name='impuesto_edit'),
    
    # Comprobantes
    path('comprobantes/', comprobante_list, name='comprobante_list'),
    path('comprobantes/crear/', comprobante_create, name='comprobante_create'),
    path('comprobantes/<int:pk>/', comprobante_detail, name='comprobante_detail'),
    path('comprobantes/<int:pk>/emitir/', comprobante_emitir, name='comprobante_emitir'),
    path('comprobantes/<int:pk>/anular/', comprobante_anular, name='comprobante_anular'),
    
    # Reportes
    path('reportes/libro-diario/', reporte_libro_diario, name='reporte_libro_diario'),
    path('reportes/libro-mayor/', reporte_libro_mayor, name='reporte_libro_mayor'),
    path('reportes/balance-general/', reporte_balance_general, name='reporte_balance_general'),
    path('reportes/estado-resultados/', reporte_estado_resultados, name='reporte_estado_resultados'),
]