from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoriaEcommerceViewSet, ProductoEcommerceViewSet, ImagenProductoViewSet,
    CarritoViewSet, ItemCarritoViewSet, PedidoViewSet, PagoOnlineViewSet
)

router = DefaultRouter()
router.register(r'categorias', CategoriaEcommerceViewSet)
router.register(r'productos', ProductoEcommerceViewSet)
router.register(r'imagenes', ImagenProductoViewSet)
router.register(r'carritos', CarritoViewSet)
router.register(r'items', ItemCarritoViewSet)
# PedidoViewSet is registered in the main api/urls.py
router.register(r'pagos', PagoOnlineViewSet)

urlpatterns = [
    path('', include(router.urls)),
]