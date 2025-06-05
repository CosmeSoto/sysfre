from django.urls import path
from .views import (
    home, ProductoListView, ProductoDetailView, CategoriaDetailView,
    ServicioListView, ServicioDetailView, buscar, busqueda_avanzada,
    mobile_home, MobileProductoListView, MobileProductoDetailView,
    agregar_valoracion_producto, agregar_valoracion_servicio, obtener_valoraciones_producto,
    lista_deseos, agregar_a_lista_deseos, eliminar_de_lista_deseos,
    comparacion, agregar_a_comparacion, eliminar_de_comparacion, limpiar_comparacion,
    carrito_detail, carrito_agregar, carrito_actualizar, carrito_eliminar, carrito_vaciar,
    checkout, checkout_direccion, checkout_envio, checkout_pago, checkout_confirmar, checkout_completado,
    cuenta_dashboard, cuenta_pedidos, cuenta_pedido_detail,
    cuenta_direcciones, cuenta_direccion_agregar, cuenta_direccion_editar,
    cuenta_perfil, cuenta_reparaciones, cuenta_reparacion_detail,
    paypal_proceso, paypal_completado, paypal_cancelado,
    tarjeta_proceso, transferencia_instrucciones, webhook_stripe,
    api_carrito_items, api_carrito_agregar, api_carrito_actualizar, api_carrito_eliminar
)

app_name = 'ecommerce'

urlpatterns = [
    # Páginas principales
    path('', home, name='inicio'),
    path('productos/', ProductoListView.as_view(), name='producto_list'),
    path('productos/<slug:slug>/', ProductoDetailView.as_view(), name='producto_detail'),
    path('categorias/<slug:slug>/', CategoriaDetailView.as_view(), name='categoria_detail'),
    path('servicios/', ServicioListView.as_view(), name='servicios_lista'),
    path('servicios/<slug:slug>/', ServicioDetailView.as_view(), name='servicio_detalle'),
    path('buscar/', buscar, name='buscar'),
    path('busqueda-avanzada/', busqueda_avanzada, name='busqueda_avanzada'),
    
    # Versión móvil
    path('m/', mobile_home, name='mobile_home'),
    path('m/productos/', MobileProductoListView.as_view(), name='mobile_producto_list'),
    path('m/productos/<slug:slug>/', MobileProductoDetailView.as_view(), name='mobile_producto_detail'),
    
    # Valoraciones
    path('valoracion/producto/<int:producto_id>/', agregar_valoracion_producto, name='agregar_valoracion_producto'),
    path('valoracion/servicio/<int:servicio_id>/', agregar_valoracion_servicio, name='agregar_valoracion_servicio'),
    path('valoracion/servicio/<int:servicio_id>/reparacion/<int:reparacion_id>/', agregar_valoracion_servicio, name='agregar_valoracion_servicio_reparacion'), # Assuming this uses the same view
    path('api/valoraciones/producto/<int:producto_id>/', obtener_valoraciones_producto, name='api_valoraciones_producto'),
    
    # Lista de deseos
    path('lista-deseos/', lista_deseos, name='lista_deseos'),
    path('lista-deseos/agregar/', agregar_a_lista_deseos, name='agregar_a_lista_deseos'),
    path('lista-deseos/eliminar/<int:item_id>/', eliminar_de_lista_deseos, name='eliminar_de_lista_deseos'),
    
    # Comparación
    path('comparacion/', comparacion, name='comparacion'),
    path('comparacion/agregar/', agregar_a_comparacion, name='agregar_a_comparacion'),
    path('comparacion/eliminar/<int:producto_id>/', eliminar_de_comparacion, name='eliminar_de_comparacion'),
    path('comparacion/limpiar/', limpiar_comparacion, name='limpiar_comparacion'),
    
    # Carrito
    path('carrito/', carrito_detail, name='carrito_detail'),
    path('carrito/agregar/', carrito_agregar, name='agregar_al_carrito'),
    path('carrito/actualizar/<int:item_id>/', carrito_actualizar, name='carrito_actualizar'),
    path('carrito/eliminar/<int:item_id>/', carrito_eliminar, name='carrito_eliminar'),
    path('carrito/vaciar/', carrito_vaciar, name='carrito_vaciar'),
    
    # Checkout
    path('checkout/', checkout, name='checkout'),
    path('checkout/direccion/', checkout_direccion, name='checkout_direccion'),
    path('checkout/envio/', checkout_envio, name='checkout_envio'),
    path('checkout/pago/', checkout_pago, name='checkout_pago'),
    path('checkout/confirmar/', checkout_confirmar, name='checkout_confirmar'),
    path('checkout/completado/<str:numero_pedido>/', checkout_completado, name='checkout_completado'),
    
    # Cuenta de cliente
    path('cuenta/', cuenta_dashboard, name='cuenta_dashboard'),
    path('cuenta/pedidos/', cuenta_pedidos, name='cuenta_pedidos'),
    path('cuenta/pedidos/<str:numero_pedido>/', cuenta_pedido_detail, name='cuenta_pedido_detail'),
    path('cuenta/direcciones/', cuenta_direcciones, name='cuenta_direcciones'),
    path('cuenta/direcciones/agregar/', cuenta_direccion_agregar, name='cuenta_direccion_agregar'),
    path('cuenta/direcciones/editar/<int:pk>/', cuenta_direccion_editar, name='cuenta_direccion_editar'),
    path('cuenta/perfil/', cuenta_perfil, name='cuenta_perfil'),
    path('cuenta/reparaciones/', cuenta_reparaciones, name='cuenta_reparaciones'),
    path('cuenta/reparaciones/<str:numero>/', cuenta_reparacion_detail, name='cuenta_reparacion_detail'),
    
    # Pasarelas de pago
    path('pago/paypal/proceso/', paypal_proceso, name='paypal_proceso'),
    path('pago/paypal/completado/', paypal_completado, name='paypal_completado'),
    path('pago/paypal/cancelado/', paypal_cancelado, name='paypal_cancelado'),
    path('pago/tarjeta/proceso/', tarjeta_proceso, name='tarjeta_proceso'),
    path('pago/transferencia/instrucciones/', transferencia_instrucciones, name='transferencia_instrucciones'),
    path('pago/webhook/stripe/', webhook_stripe, name='webhook_stripe'),
    
    # API para carrito
    path('api/carrito/items/', api_carrito_items, name='api_carrito_items'),
    path('api/carrito/agregar/', api_carrito_agregar, name='api_carrito_agregar'),
    path('api/carrito/actualizar/', api_carrito_actualizar, name='api_carrito_actualizar'),
    path('api/carrito/eliminar/', api_carrito_eliminar, name='api_carrito_eliminar'),
]