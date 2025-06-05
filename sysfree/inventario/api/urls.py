from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoriaViewSet, ProductoViewSet, ProveedorViewSet, MovimientoInventarioViewSet

router = DefaultRouter()
# CategoriaViewSet is registered in the main api/urls.py
# ProductoViewSet is registered in the main api/urls.py
router.register(r'proveedores', ProveedorViewSet)
router.register(r'movimientos', MovimientoInventarioViewSet)

urlpatterns = [
    path('', include(router.urls)),
]