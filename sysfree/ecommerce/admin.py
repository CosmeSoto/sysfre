from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    CategoriaEcommerce, ProductoEcommerce, ImagenProducto,
    Carrito, ItemCarrito, Pedido, DetallePedido,
    PagoOnline, ConfiguracionTienda, ServicioEcommerce
)


@admin.register(CategoriaEcommerce)
class CategoriaEcommerceAdmin(admin.ModelAdmin):
    """Admin para categorías de la tienda."""
    list_display = ('nombre', 'slug', 'categoria_padre', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre', 'descripcion')
    prepopulated_fields = {'slug': ('nombre',)}


class ImagenProductoInline(admin.TabularInline):
    """Inline para imágenes de producto."""
    model = ImagenProducto
    extra = 1


@admin.register(ProductoEcommerce)
class ProductoEcommerceAdmin(admin.ModelAdmin):
    """Admin para productos de la tienda."""
    list_display = ('producto', 'destacado', 'nuevo', 'oferta', 'precio_actual')
    list_filter = ('destacado', 'nuevo', 'oferta')
    search_fields = ('producto__nombre', 'producto__codigo', 'descripcion_corta')
    inlines = [ImagenProductoInline]
    filter_horizontal = ('categorias',)
    fieldsets = (
        (None, {
            'fields': ('producto', 'slug', 'categorias')
        }),
        (_('Descripciones'), {
            'fields': ('descripcion_corta', 'descripcion_larga')
        }),
        (_('SEO'), {
            'fields': ('meta_titulo', 'meta_descripcion', 'meta_keywords')
        }),
        (_('Destacados'), {
            'fields': ('destacado', 'nuevo', 'orden')
        }),
        (_('Ofertas'), {
            'fields': ('oferta', 'precio_oferta', 'fecha_inicio_oferta', 'fecha_fin_oferta')
        }),
    )
    readonly_fields = ('visitas', 'ventas')


@admin.register(ServicioEcommerce)
class ServicioEcommerceAdmin(admin.ModelAdmin):
    """Admin para servicios de la tienda."""
    list_display = ('servicio', 'destacado', 'nuevo', 'oferta', 'precio_actual')
    list_filter = ('destacado', 'nuevo', 'oferta')
    search_fields = ('servicio__nombre', 'descripcion_corta')
    filter_horizontal = ('categorias',)
    fieldsets = (
        (None, {
            'fields': ('servicio', 'slug', 'categorias')
        }),
        (_('Descripciones'), {
            'fields': ('descripcion_corta', 'descripcion_larga')
        }),
        (_('SEO'), {
            'fields': ('meta_titulo', 'meta_descripcion', 'meta_keywords')
        }),
        (_('Destacados'), {
            'fields': ('destacado', 'nuevo', 'orden')
        }),
        (_('Ofertas'), {
            'fields': ('oferta', 'precio_oferta', 'fecha_inicio_oferta', 'fecha_fin_oferta')
        }),
    )
    readonly_fields = ('visitas',)


class DetallePedidoInline(admin.TabularInline):
    """Inline para detalles de pedido."""
    model = DetallePedido
    extra = 0
    readonly_fields = ('producto', 'es_servicio', 'cantidad', 'precio_unitario', 
                      'impuesto_unitario', 'subtotal', 'impuestos', 'total', 'reparacion')


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    """Admin para pedidos."""
    list_display = ('numero', 'cliente', 'fecha', 'estado', 'total')
    list_filter = ('estado', 'fecha')
    search_fields = ('numero', 'cliente__nombre', 'cliente__email')
    date_hierarchy = 'fecha'
    inlines = [DetallePedidoInline]
    readonly_fields = ('numero', 'cliente', 'carrito', 'fecha', 'subtotal', 
                      'impuestos', 'total', 'fecha_pago', 'fecha_envio', 'fecha_entrega')
    fieldsets = (
        (None, {
            'fields': ('numero', 'cliente', 'fecha', 'estado')
        }),
        (_('Direcciones'), {
            'fields': ('direccion_facturacion', 'direccion_envio')
        }),
        (_('Totales'), {
            'fields': ('subtotal', 'impuestos', 'envio', 'descuento', 'total')
        }),
        (_('Seguimiento'), {
            'fields': ('fecha_pago', 'fecha_envio', 'fecha_entrega', 'codigo_seguimiento')
        }),
        (_('Facturación'), {
            'fields': ('factura', 'notas')
        }),
    )


@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    """Admin para carritos."""
    list_display = ('id', 'cliente', 'fecha_actualizacion', 'total_items', 'total', 'convertido_a_pedido')
    list_filter = ('convertido_a_pedido', 'fecha_creacion')
    search_fields = ('cliente__nombre', 'cliente__email', 'sesion_id')
    date_hierarchy = 'fecha_actualizacion'
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')


class ItemCarritoAdmin(admin.ModelAdmin):
    """Admin para items de carrito."""
    list_display = ('carrito', 'producto', 'es_servicio', 'cantidad', 'precio_unitario', 'total')
    list_filter = ('es_servicio',)
    search_fields = ('carrito__cliente__nombre', 'producto__nombre')


@admin.register(PagoOnline)
class PagoOnlineAdmin(admin.ModelAdmin):
    """Admin para pagos online."""
    list_display = ('pedido', 'referencia', 'metodo', 'estado', 'monto', 'fecha')
    list_filter = ('metodo', 'estado', 'fecha')
    search_fields = ('pedido__numero', 'referencia')
    date_hierarchy = 'fecha'
    readonly_fields = ('fecha',)


@admin.register(ConfiguracionTienda)
class ConfiguracionTiendaAdmin(admin.ModelAdmin):
    """Admin para configuración de la tienda."""
    list_display = ('nombre_tienda', 'activo')
    fieldsets = (
        (None, {
            'fields': ('nombre_tienda', 'logo', 'favicon', 'activo')
        }),
        (_('Contacto'), {
            'fields': ('email_contacto', 'telefono_contacto', 'direccion')
        }),
        (_('Redes sociales'), {
            'fields': ('facebook', 'instagram', 'twitter', 'youtube')
        }),
        (_('SEO'), {
            'fields': ('meta_titulo', 'meta_descripcion', 'meta_keywords')
        }),
        (_('Configuración de envíos'), {
            'fields': ('envio_gratis_desde',)
        }),
    )