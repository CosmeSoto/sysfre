from .home_views import home
from .producto_views import ProductoListView, ProductoDetailView, CategoriaDetailView
from .servicio_views import ServicioListView, ServicioDetailView
from .busqueda_views import buscar
from .busqueda_avanzada_views import busqueda_avanzada # Added import
from .mobile_views import mobile_home, MobileProductoListView, MobileProductoDetailView # Added import
from .carrito_views import (
    carrito_detail, carrito_agregar, carrito_actualizar,
    carrito_eliminar, carrito_vaciar,
    api_carrito_items, api_carrito_agregar,
    api_carrito_actualizar, api_carrito_eliminar
)
from .checkout_views import (
    checkout, checkout_direccion, checkout_envio,
    checkout_pago, checkout_confirmar, checkout_completado
)
from .cuenta_views import (
    cuenta_dashboard, cuenta_pedidos, cuenta_pedido_detail,
    cuenta_direcciones, cuenta_direccion_agregar, cuenta_direccion_editar,
    cuenta_perfil, cuenta_reparaciones, cuenta_reparacion_detail
)
from .pago_views import (
    paypal_proceso, paypal_completado, paypal_cancelado,
    tarjeta_proceso, transferencia_instrucciones, webhook_stripe # Added webhook_stripe
)
from .valoracion_views import (
    agregar_valoracion_producto, agregar_valoracion_servicio,
    obtener_valoraciones_producto
)
from .lista_deseos_views import (
    lista_deseos, agregar_a_lista_deseos, eliminar_de_lista_deseos
)
from .comparacion_views import (
    comparacion, agregar_a_comparacion, eliminar_de_comparacion,
    limpiar_comparacion
)

__all__ = [
    'home',
    'ProductoListView',
    'ProductoDetailView',
    'CategoriaDetailView',
    'ServicioListView',
    'ServicioDetailView',
    'buscar',
    'busqueda_avanzada', # Added to __all__
    'mobile_home', # Added to __all__
    'MobileProductoListView', # Added to __all__
    'MobileProductoDetailView', # Added to __all__
    'carrito_detail',
    'carrito_agregar',
    'carrito_actualizar',
    'carrito_eliminar',
    'carrito_vaciar',
    'api_carrito_items',
    'api_carrito_agregar',
    'api_carrito_actualizar',
    'api_carrito_eliminar',
    'checkout',
    'checkout_direccion',
    'checkout_envio',
    'checkout_pago',
    'checkout_confirmar',
    'checkout_completado',
    'cuenta_dashboard',
    'cuenta_pedidos',
    'cuenta_pedido_detail',
    'cuenta_direcciones',
    'cuenta_direccion_agregar',
    'cuenta_direccion_editar',
    'cuenta_perfil',
    'cuenta_reparaciones',
    'cuenta_reparacion_detail',
    'paypal_proceso',
    'paypal_completado',
    'paypal_cancelado',
    'tarjeta_proceso',
    'transferencia_instrucciones',
    'webhook_stripe', # Added to __all__
    'agregar_valoracion_producto',
    'agregar_valoracion_servicio',
    'obtener_valoraciones_producto',
    'lista_deseos',
    'agregar_a_lista_deseos',
    'eliminar_de_lista_deseos',
    'comparacion',
    'agregar_a_comparacion',
    'eliminar_de_comparacion',
    'limpiar_comparacion',
]