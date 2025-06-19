from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    CategoriaEcommerce, ProductoEcommerce, ImagenProducto,
    Carrito, ItemCarrito, Pedido, DetallePedido,
    PagoOnline, ConfiguracionTienda, ServicioEcommerce,
    Valoracion, ListaDeseos
)

@admin.register(CategoriaEcommerce)
class CategoriaEcommerceAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug', 'categoria_padre', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre', 'descripcion')
    prepopulated_fields = {'slug': ('nombre',)}
    autocomplete_fields = ['categoria_padre']
    ordering = ('nombre',)

class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 1

@admin.register(ProductoEcommerce)
class ProductoEcommerceAdmin(admin.ModelAdmin):
    list_display = ('producto', 'destacado', 'nuevo', 'oferta', 'precio_actual')
    list_filter = ('destacado', 'nuevo', 'oferta', 'categorias')
    search_fields = ('producto__nombre', 'producto__codigo', 'descripcion_corta')
    inlines = [ImagenProductoInline]
    filter_horizontal = ('categorias',)
    autocomplete_fields = ['producto']
    ordering = ('producto__nombre',)
    fieldsets = (
        (None, {'fields': ('producto', 'slug', 'categorias')}),
        (_('Descripciones'), {'fields': ('descripcion_corta', 'descripcion_larga')}),
        (_('SEO'), {'fields': ('meta_titulo', 'meta_descripcion', 'meta_keywords')}),
        (_('Destacados'), {'fields': ('destacado', 'nuevo', 'orden')}),
        (_('Ofertas'), {'fields': ('oferta', 'precio_oferta', 'fecha_inicio_oferta', 'fecha_fin_oferta')}),
        (_('Auditoría'), {'fields': ('visitas', 'ventas')}),
    )
    readonly_fields = ('visitas', 'ventas')

@admin.register(ServicioEcommerce)
class ServicioEcommerceAdmin(admin.ModelAdmin):
    list_display = ('servicio', 'destacado', 'nuevo', 'oferta', 'precio_actual')
    list_filter = ('destacado', 'nuevo', 'oferta', 'categorias')
    search_fields = ('servicio__nombre', 'descripcion_corta')
    filter_horizontal = ('categorias',)
    autocomplete_fields = ['servicio']
    ordering = ('servicio__nombre',)
    fieldsets = (
        (None, {'fields': ('servicio', 'slug', 'categorias')}),
        (_('Descripciones'), {'fields': ('descripcion_corta', 'descripcion_larga')}),
        (_('SEO'), {'fields': ('meta_titulo', 'meta_descripcion', 'meta_keywords')}),
        (_('Destacados'), {'fields': ('destacado', 'nuevo', 'orden')}),
        (_('Ofertas'), {'fields': ('oferta', 'precio_oferta', 'fecha_inicio_oferta', 'fecha_fin_oferta')}),
        (_('Auditoría'), {'fields': ('visitas',)}),
    )
    readonly_fields = ('visitas',)

class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0
    readonly_fields = ('producto', 'item', 'cantidad', 'precio_unitario',
                      'impuesto_unitario', 'subtotal', 'impuestos', 'total', 'reparacion')
    autocomplete_fields = ['producto', 'reparacion']
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('numero', 'cliente', 'fecha', 'estado', 'total')
    list_filter = ('estado',)
    search_fields = ('numero', 'cliente__nombres', 'cliente__email')
    date_hierarchy = 'fecha'
    inlines = [DetallePedidoInline]
    ordering = ('-fecha',)
    autocomplete_fields = ['cliente', 'carrito', 'factura', 'direccion_facturacion', 'direccion_envio']
    readonly_fields = ('numero', 'fecha', 'subtotal', 'impuestos', 'total', 'fecha_pago', 'fecha_envio', 'fecha_entrega')
    fieldsets = (
        (None, {'fields': ('numero', 'cliente', 'fecha', 'estado')}),
        (_('Direcciones'), {'fields': ('direccion_facturacion', 'direccion_envio')}),
        (_('Totales'), {'fields': ('subtotal', 'impuestos', 'envio', 'descuento', 'total')}),
        (_('Seguimiento'), {'fields': ('fecha_pago', 'fecha_envio', 'fecha_entrega', 'codigo_seguimiento')}),
        (_('Facturación'), {'fields': ('factura', 'notas')}),
        (_('Referencias'), {'fields': ('carrito',)}),
    )

class ItemCarritoInline(admin.TabularInline):
    model = ItemCarrito
    extra = 0
    autocomplete_fields = ['producto']

@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha_actualizacion', 'total_items', 'total', 'convertido_a_pedido')
    list_filter = ('convertido_a_pedido',)
    search_fields = ('cliente__nombres', 'cliente__email', 'sesion_id')
    date_hierarchy = 'fecha_actualizacion'
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion', 'total_items', 'total')
    autocomplete_fields = ['cliente']
    inlines = [ItemCarritoInline]

@admin.register(ItemCarrito)
class ItemCarritoAdmin(admin.ModelAdmin):
    list_display = ('carrito', 'item', 'cantidad', 'precio_unitario', 'total')
    list_filter = ('carrito__convertido_a_pedido',)
    search_fields = ('carrito__cliente__nombres', 'producto__nombre')
    autocomplete_fields = ['carrito', 'producto']

@admin.register(PagoOnline)
class PagoOnlineAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'referencia', 'metodo', 'estado', 'monto', 'fecha')
    list_filter = ('metodo', 'estado')
    search_fields = ('pedido__numero', 'referencia')
    date_hierarchy = 'fecha'
    readonly_fields = ('fecha',)
    autocomplete_fields = ['pedido']

@admin.register(ConfiguracionTienda)
class ConfiguracionTiendaAdmin(admin.ModelAdmin):
    list_display = ('nombre_tienda', 'activo')
    def has_add_permission(self, request):
        return not ConfiguracionTienda.objects.exists()
    fieldsets = (
        (None, {'fields': ('nombre_tienda', 'logo', 'favicon', 'activo')}),
        (_('Contacto'), {'fields': ('email_contacto', 'telefono_contacto', 'direccion')}),
        (_('Redes sociales'), {'fields': ('facebook', 'instagram', 'twitter', 'youtube')}),
        (_('SEO'), {'fields': ('meta_titulo', 'meta_descripcion', 'meta_keywords')}),
        (_('Configuración de envíos'), {'fields': ('envio_gratis_desde',)}),
    )

@admin.register(Valoracion)
class ValoracionAdmin(admin.ModelAdmin):
    list_display = ('producto', 'cliente', 'puntuacion', 'fecha', 'aprobado')
    list_filter = ('aprobado', 'puntuacion')
    search_fields = ('producto__nombre', 'cliente__nombres', 'comentario')
    autocomplete_fields = ['producto', 'cliente']
    actions = ['aprobar_valoraciones']

    def aprobar_valoraciones(self, request, queryset):
        queryset.update(aprobado=True)
    aprobar_valoraciones.short_description = _("Aprobar valoraciones seleccionadas")

@admin.register(ListaDeseos)
class ListaDeseosAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'nombre', 'total_items')
    search_fields = ('cliente__nombres', 'nombre')
    autocomplete_fields = ['cliente']