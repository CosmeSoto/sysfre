# Configuración de SimpleUI para el panel de administración de SysFree

# Logo del sistema (asegúrate de que la ruta sea correcta en tu proyecto)
SIMPLEUI_LOGO = '/static/favicon.ico'

# Título del sistema
SIMPLEUI_TITLE = 'SysFree - Panel de Administración'

# Tema de SimpleUI (admin.lte.css para un diseño profesional y limpio)
SIMPLEUI_DEFAULT_THEME = 'admin.lte.css'

# Configuración de la página de inicio
SIMPLEUI_HOME_TITLE = 'Panel de SysFree'
SIMPLEUI_HOME_ICON = 'fas fa-store'  # Icono representativo para el sistema
SIMPLEUI_HOME_INFO = False  # Ocultar información rápida para un diseño limpio
SIMPLEUI_HOME_QUICK = True  # Mostrar acciones rápidas
SIMPLEUI_HOME_ACTION = True  # Permitir acciones en la página de inicio
# SIMPLEUI_HOME_PAGE = '/admin/reportes/reporte/'  # Enlace a reportes para estadísticas

# Deshabilitar análisis para mejorar la privacidad
SIMPLEUI_ANALYSIS = False

# Ocultar botón de ayuda
SIMPLEUI_HELP_URL = False

# Configuración del menú
SIMPLEUI_CONFIG = {
    'system_keep': False,  # No mostrar menús automáticos de Django
    'menu_display': [
        'Core',
        'Clientes',
        'Inventario',
        'Ventas',
        'Tienda Online',
        'Reparaciones',
        'Contabilidad',
        'Reportes',
        'Seguridad',
    ],
    'dynamic': True,  # Permitir configuración dinámica
    'menus': [
        {
            'name': 'Core',
            'icon': 'fas fa-cogs',
            'models': [
                {'name': 'Usuarios', 'icon': 'fas fa-users', 'url': 'core/usuario/'},
                {'name': 'Configuraciones', 'icon': 'fas fa-sliders-h', 'url': 'core/configuracionsistema/'},
                {'name': 'Empresas', 'icon': 'fas fa-building', 'url': 'core/empresa/'},
                {'name': 'Sucursales', 'icon': 'fas fa-store', 'url': 'core/sucursal/'},
                {'name': 'Logs de Actividad', 'icon': 'fas fa-history', 'url': 'core/logactividad/'},
            ],
        },
        {
            'name': 'Clientes',
            'icon': 'fas fa-user-friends',
            'models': [
                {'name': 'Clientes', 'icon': 'fas fa-user', 'url': 'clientes/cliente/'},
                # {'name': 'Contactos', 'icon': 'fas fa-address-book', 'url': 'clientes/contactocliente/'},
                # {'name': 'Direcciones', 'icon': 'fas fa-map-marker-alt', 'url': 'clientes/direccioncliente/'},
            ],
        },
        {
            'name': 'Inventario',
            'icon': 'fas fa-warehouse',
            'models': [
                {'name': 'Categorías', 'icon': 'fas fa-tags', 'url': 'inventario/categoria/'},
                {'name': 'Productos', 'icon': 'fas fa-box', 'url': 'inventario/producto/'},
                {'name': 'Proveedores', 'icon': 'fas fa-truck', 'url': 'inventario/proveedor/'},
                {'name': 'Movimientos', 'icon': 'fas fa-exchange-alt', 'url': 'inventario/movimientoinventario/'},
                {'name': 'Almacenes', 'icon': 'fas fa-building', 'url': 'inventario/almacen/'},
                {'name': 'Contactos de Proveedores', 'icon': 'fas fa-address-book', 'url': 'inventario/contactoproveedor/'},
                {'name': 'Lotes', 'icon': 'fas fa-cubes', 'url': 'inventario/lote/'},
                {'name': 'Órdenes de Compra', 'icon': 'fas fa-file-invoice', 'url': 'inventario/ordencompra/'},
                {'name': 'Stock por Almacén', 'icon': 'fas fa-inventory', 'url': 'inventario/stockalmacen/'},
                {'name': 'Atributos', 'icon': 'fas fa-cog', 'url': 'inventario/atributo/'},
                {'name': 'Valores de Atributos', 'icon': 'fas fa-list-alt', 'url': 'inventario/valoratributo/'},
                {'name': 'Variaciones', 'icon': 'fas fa-list-ul', 'url': 'inventario/variacion/'},
            ],
        },
        {
            'name': 'Ventas',
            'icon': 'fas fa-shopping-cart',
            'models': [
                {'name': 'Ventas', 'icon': 'fas fa-receipt', 'url': 'ventas/venta/'},
                {'name': 'Pagos', 'icon': 'fas fa-credit-card', 'url': 'ventas/pago/'},
                {'name': 'Proformas', 'icon': 'fas fa-file-invoice', 'url': 'ventas/proforma/'},
            ],
        },
        {
            'name': 'Tienda Online',
            'icon': 'fas fa-shopping-bag',
            'models': [
                {
                    'name': 'Catálogo',
                    'icon': 'fas fa-tags',
                    'models': [
                        {'name': 'Categorías', 'icon': 'fas fa-tags', 'url': 'ecommerce/categoriaecommerce/'},
                        {'name': 'Productos', 'icon': 'fas fa-box', 'url': 'ecommerce/productoecommerce/'},
                        {'name': 'Servicios', 'icon': 'fas fa-tools', 'url': 'ecommerce/servicioecommerce/'},
                        {'name': 'Imágenes de Productos', 'icon': 'fas fa-image', 'url': 'ecommerce/imagenproducto/'},
                    ],
                },
                {
                    'name': 'Carrito y Pedidos',
                    'icon': 'fas fa-shopping-cart',
                    'models': [
                        {'name': 'Carritos', 'icon': 'fas fa-shopping-cart', 'url': 'ecommerce/carrito/'},
                        {'name': 'Ítems de Carrito', 'icon': 'fas fa-list', 'url': 'ecommerce/itemcarrito/'},
                        {'name': 'Pedidos', 'icon': 'fas fa-clipboard-list', 'url': 'ecommerce/pedido/'},
                        {'name': 'Detalles de Pedido', 'icon': 'fas fa-receipt', 'url': 'ecommerce/detallepedido/'},
                    ],
                },
                {
                    'name': 'Pagos y Valoraciones',
                    'icon': 'fas fa-credit-card',
                    'models': [
                        {'name': 'Pagos Online', 'icon': 'fas fa-credit-card', 'url': 'ecommerce/pagoonline/'},
                        {'name': 'Valoraciones de Productos', 'icon': 'fas fa-star', 'url': 'ecommerce/valoracion/'},
                        {'name': 'Valoraciones de Servicios', 'icon': 'fas fa-star-half-alt', 'url': 'ecommerce/valoracionservicio/'},
                    ],
                },
                {
                    'name': 'Otros',
                    'icon': 'fas fa-cog',
                    'models': [
                        {'name': 'Configuración Tienda', 'icon': 'fas fa-cog', 'url': 'ecommerce/configuraciontienda/'},
                        {'name': 'Comparaciones', 'icon': 'fas fa-balance-scale', 'url': 'ecommerce/comparacion/'},
                        {'name': 'Listas de Deseos', 'icon': 'fas fa-heart', 'url': 'ecommerce/listadeseos/'},
                        {'name': 'Ítems de Lista de Deseos', 'icon': 'fas fa-list-ul', 'url': 'ecommerce/itemlistadeseos/'},
                    ],
                },
            ],
        },
        {
            'name': 'Reparaciones',
            'icon': 'fas fa-tools',
            'models': [
                {'name': 'Servicios', 'icon': 'fas fa-wrench', 'url': 'reparaciones/servicioreparacion/'},
                {
                    'name': 'Reparaciones',
                    'icon': 'fas fa-tools',
                    'models': [
                        {'name': 'Reparaciones', 'icon': 'fas fa-tools', 'url': 'reparaciones/reparacion/'},
                        {'name': 'Seguimientos', 'icon': 'fas fa-history', 'url': 'reparaciones/seguimientoreparacion/'},
                        {'name': 'Repuestos', 'icon': 'fas fa-cogs', 'url': 'reparaciones/repuestoreparacion/'},
                    ],
                },
            ],
        },
        {
            'name': 'Contabilidad',
            'icon': 'fas fa-file-invoice-dollar',
            'models': [
                {'name': 'Impuestos', 'icon': 'fas fa-percentage', 'url': 'fiscal/impuesto/'},
                {'name': 'Periodos Fiscales', 'icon': 'fas fa-calendar-alt', 'url': 'fiscal/periodofiscal/'},
                {'name': 'Cuentas Contables', 'icon': 'fas fa-book', 'url': 'fiscal/cuentacontable/'},
                {'name': 'Asientos Contables', 'icon': 'fas fa-balance-scale', 'url': 'fiscal/asientocontable/'},
                {'name': 'Líneas de Asiento', 'icon': 'fas fa-list-alt', 'url': 'fiscal/lineaasiento/'},
                {'name': 'Comprobantes', 'icon': 'fas fa-file-invoice', 'url': 'fiscal/comprobante/'},
            ],
        },
        {
            'name': 'Reportes',
            'icon': 'fas fa-chart-bar',
            'models': [
                {'name': 'Reportes', 'icon': 'fas fa-file-alt', 'url': 'reportes/reporte/'},
                {
                    'name': 'Gestión de Reportes',
                    'icon': 'fas fa-cog',
                    'models': [
                        {'name': 'Programaciones', 'icon': 'fas fa-clock', 'url': 'reportes/programacionreporte/'},
                        {'name': 'Historial', 'icon': 'fas fa-history', 'url': 'reportes/historialreporte/'},
                    ],
                },
            ],
        },
        {
            'name': 'Seguridad',
            'icon': 'fas fa-shield-alt',
            'models': [
                {'name': 'Grupos', 'icon': 'fas fa-users-cog', 'url': 'auth/group/'},
                {'name': 'Permisos', 'icon': 'fas fa-key', 'url': 'auth/permission/'},
            ],
        },
    ],
}

# Configuración de iconos para modelos
SIMPLEUI_ICON = {
    # Modelos de la aplicación core
    'core.Usuario': 'fas fa-user',
    'core.ConfiguracionSistema': 'fas fa-sliders-h',
    'core.Empresa': 'fas fa-building',
    'core.Sucursal': 'fas fa-store',
    'core.LogActividad': 'fas fa-history',
    # Modelos de la aplicación clientes
    'clientes.Cliente': 'fas fa-user',
    'clientes.ContactoCliente': 'fas fa-address-book',
    'clientes.DireccionCliente': 'fas fa-map-marker-alt',
    # Modelos de la aplicación ecommerce
    'ecommerce.CategoriaEcommerce': 'fas fa-tags',
    'ecommerce.ProductoEcommerce': 'fas fa-box',
    'ecommerce.ServicioEcommerce': 'fas fa-tools',
    'ecommerce.ImagenProducto': 'fas fa-image',
    'ecommerce.ConfiguracionTienda': 'fas fa-cog',
    'ecommerce.Carrito': 'fas fa-shopping-cart',
    'ecommerce.ItemCarrito': 'fas fa-list',
    'ecommerce.Pedido': 'fas fa-clipboard-list',
    'ecommerce.DetallePedido': 'fas fa-receipt',
    'ecommerce.PagoOnline': 'fas fa-credit-card',
    'ecommerce.Valoracion': 'fas fa-star',
    'ecommerce.ValoracionServicio': 'fas fa-star-half-alt',
    'ecommerce.Comparacion': 'fas fa-balance-scale',
    'ecommerce.ListaDeseos': 'fas fa-heart',
    'ecommerce.ItemListaDeseos': 'fas fa-list-ul',
    # Modelos de la aplicación fiscal
    'fiscal.Impuesto': 'fas fa-percentage',
    'fiscal.PeriodoFiscal': 'fas fa-calendar-alt',
    'fiscal.CuentaContable': 'fas fa-book',
    'fiscal.AsientoContable': 'fas fa-balance-scale',
    'fiscal.LineaAsiento': 'fas fa-list-alt',
    'fiscal.Comprobante': 'fas fa-file-invoice',
    # Modelos de la aplicación inventario
    'inventario.Categoria': 'fas fa-tags',
    'inventario.Producto': 'fas fa-box',
    'inventario.Proveedor': 'fas fa-truck',
    'inventario.MovimientoInventario': 'fas fa-exchange-alt',
    'inventario.Almacen': 'fas fa-building',
    'inventario.ContactoProveedor': 'fas fa-address-book',
    'inventario.Lote': 'fas fa-cubes',
    'inventario.OrdenCompra': 'fas fa-file-invoice',
    'inventario.StockAlmacen': 'fas fa-inventory',
    'inventario.Atributo': 'fas fa-cog',
    'inventario.ValorAtributo': 'fas fa-list-alt',
    'inventario.Variacion': 'fas fa-list-ul',
    # Modelos de la aplicación reparaciones
    'reparaciones.ServicioReparacion': 'fas fa-wrench',
    'reparaciones.Reparacion': 'fas fa-tools',
    'reparaciones.SeguimientoReparacion': 'fas fa-history',
    'reparaciones.RepuestoReparacion': 'fas fa-cogs',
    # Modelos de la aplicación reportes
    'reportes.Reporte': 'fas fa-file-alt',
    'reportes.ProgramacionReporte': 'fas fa-clock',
    'reportes.HistorialReporte': 'fas fa-history',
    # Modelos de la aplicación ventas
    'ventas.Venta': 'fas fa-receipt',
    'ventas.DetalleVenta': 'fas fa-list',
    'ventas.Pago': 'fas fa-credit-card',
    'ventas.Proforma': 'fas fa-file-invoice',
    'ventas.DetalleProforma': 'fas fa-list-alt',
}