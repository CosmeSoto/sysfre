from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoriaViewSet, ProductoViewSet, ProveedorViewSet, MovimientoInventarioViewSet,
    AlmacenViewSet, LoteViewSet, StockAlmacenViewSet, ContactoProveedorViewSet,
    OrdenCompraViewSet, ItemOrdenCompraViewSet, VariacionViewSet, AlertaStockViewSet
)

router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet)
router.register(r'productos', ProductoViewSet)
router.register(r'proveedores', ProveedorViewSet)
router.register(r'movimientos', MovimientoInventarioViewSet)
router.register(r'almacenes', AlmacenViewSet)
router.register(r'lotes', LoteViewSet)
router.register(r'stock-almacen', StockAlmacenViewSet)
router.register(r'contactos-proveedor', ContactoProveedorViewSet)
router.register(r'ordenes-compra', OrdenCompraViewSet)
router.register(r'items-orden-compra', ItemOrdenCompraViewSet)
router.register(r'variaciones', VariacionViewSet)
router.register(r'alertas-stock', AlertaStockViewSet)

urlpatterns = [
    path('', include(router.urls)),
]