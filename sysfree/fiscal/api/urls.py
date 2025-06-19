from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PeriodoFiscalViewSet, CuentaContableViewSet,
    AsientoContableViewSet, LineaAsientoViewSet, ComprobanteViewSet,
    TipoIVAViewSet, RetencionViewSet, ComprobanteRetencionViewSet
)

router = DefaultRouter()
router.register(r'periodos', PeriodoFiscalViewSet)
router.register(r'cuentas', CuentaContableViewSet)
router.register(r'asientos', AsientoContableViewSet)
router.register(r'lineas', LineaAsientoViewSet)
router.register(r'comprobantes', ComprobanteViewSet)
router.register(r'impuestos', TipoIVAViewSet, basename='impuesto')
router.register(r'retenciones', RetencionViewSet, basename='retencion')
router.register(r'comprobantes-retencion', ComprobanteRetencionViewSet, basename='comprobanteretencion')

urlpatterns = [
    path('', include(router.urls)),
]