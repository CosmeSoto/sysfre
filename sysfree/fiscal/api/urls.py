from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PeriodoFiscalViewSet, CuentaContableViewSet,
    AsientoContableViewSet, LineaAsientoViewSet, ComprobanteViewSet
)

router = DefaultRouter()
router.register(r'periodos', PeriodoFiscalViewSet)
router.register(r'cuentas', CuentaContableViewSet)
router.register(r'asientos', AsientoContableViewSet)
router.register(r'lineas', LineaAsientoViewSet)
router.register(r'comprobantes', ComprobanteViewSet)

urlpatterns = [
    path('', include(router.urls)),
]