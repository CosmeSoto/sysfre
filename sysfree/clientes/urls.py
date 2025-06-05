from django.urls import path
from .views import (
    cliente_list, cliente_create, cliente_detail, cliente_edit,
    contacto_create, contacto_edit, contacto_delete,
    direccion_create, direccion_edit, direccion_delete,
    portal_cliente, portal_perfil, portal_direcciones,
    portal_pedidos, portal_facturas, portal_reparaciones
)

app_name = 'clientes'

urlpatterns = [
    # Clientes
    path('', cliente_list, name='cliente_list'),
    path('crear/', cliente_create, name='cliente_create'),
    path('<int:pk>/', cliente_detail, name='cliente_detail'),
    path('<int:pk>/editar/', cliente_edit, name='cliente_edit'),
    
    # Contactos
    path('<int:cliente_id>/contactos/crear/', contacto_create, name='contacto_create'),
    path('contactos/<int:pk>/editar/', contacto_edit, name='contacto_edit'),
    path('contactos/<int:pk>/eliminar/', contacto_delete, name='contacto_delete'),
    
    # Direcciones
    path('<int:cliente_id>/direcciones/crear/', direccion_create, name='direccion_create'),
    path('direcciones/<int:pk>/editar/', direccion_edit, name='direccion_edit'),
    path('direcciones/<int:pk>/eliminar/', direccion_delete, name='direccion_delete'),
    
    # Portal de cliente
    path('portal/', portal_cliente, name='portal_cliente'),
    path('portal/perfil/', portal_perfil, name='portal_perfil'),
    path('portal/direcciones/', portal_direcciones, name='portal_direcciones'),
    path('portal/pedidos/', portal_pedidos, name='portal_pedidos'),
    path('portal/facturas/', portal_facturas, name='portal_facturas'),
    path('portal/reparaciones/', portal_reparaciones, name='portal_reparaciones'),
]