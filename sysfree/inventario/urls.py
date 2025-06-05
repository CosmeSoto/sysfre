from django.urls import path
from .views import (
    producto_list, producto_create, producto_detail, producto_update, producto_delete,
    entrada_inventario, salida_inventario,
    categoria_list, categoria_create, categoria_update,
    proveedor_list, proveedor_create, proveedor_detail, proveedor_update,
    movimiento_list
)

app_name = 'inventario'

urlpatterns = [
    # Productos
    path('productos/', producto_list, name='producto_list'),
    path('productos/nuevo/', producto_create, name='producto_create'),
    path('productos/<int:pk>/', producto_detail, name='producto_detail'),
    path('productos/<int:pk>/editar/', producto_update, name='producto_update'),
    path('productos/<int:pk>/eliminar/', producto_delete, name='producto_delete'),
    path('productos/<int:pk>/entrada/', entrada_inventario, name='entrada_inventario'),
    path('productos/<int:pk>/salida/', salida_inventario, name='salida_inventario'),
    
    # Categorías
    path('categorias/', categoria_list, name='categoria_list'),
    path('categorias/nueva/', categoria_create, name='categoria_create'),
    path('categorias/<int:pk>/editar/', categoria_update, name='categoria_update'),
    
    # Proveedores
    path('proveedores/', proveedor_list, name='proveedor_list'),
    path('proveedores/nuevo/', proveedor_create, name='proveedor_create'),
    path('proveedores/<int:pk>/', proveedor_detail, name='proveedor_detail'),
    path('proveedores/<int:pk>/editar/', proveedor_update, name='proveedor_update'),
    
    # Movimientos
    path('movimientos/', movimiento_list, name='movimiento_list'),
]