from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VentaViewSet, DetalleVentaViewSet, PagoViewSet

router = DefaultRouter()
# VentaViewSet is registered in the main api/urls.py
router.register(r'detalles', DetalleVentaViewSet)
router.register(r'pagos', PagoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]