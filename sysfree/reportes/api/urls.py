from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReporteViewSet, ProgramacionReporteViewSet, HistorialReporteViewSet
from .reportes_views import (
    ReporteVentasView, ReporteVentasPorPeriodoView, ReporteProductosMasVendidosView,
    ReporteClientesFrecuentesView, ReporteInventarioView, ReporteMovimientosInventarioView,
    ReporteProductosBajoStockView
)

router = DefaultRouter()
router.register(r'reportes', ReporteViewSet)
router.register(r'programaciones', ProgramacionReporteViewSet)
router.register(r'historial', HistorialReporteViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # Reportes específicos
    path('ventas/', ReporteVentasView.as_view(), name='reportes-ventas'),
    path('ventas-por-periodo/', ReporteVentasPorPeriodoView.as_view(), name='reportes-ventas-por-periodo'),
    path('productos-mas-vendidos/', ReporteProductosMasVendidosView.as_view(), name='reportes-productos-mas-vendidos'),
    path('clientes-frecuentes/', ReporteClientesFrecuentesView.as_view(), name='reportes-clientes-frecuentes'),
    path('inventario/', ReporteInventarioView.as_view(), name='reportes-inventario'),
    path('movimientos-inventario/', ReporteMovimientosInventarioView.as_view(), name='reportes-movimientos-inventario'),
    path('productos-bajo-stock/', ReporteProductosBajoStockView.as_view(), name='reportes-productos-bajo-stock'),
]