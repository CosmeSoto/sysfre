from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.admin import SimpleListFilter
from django.db.models import Q, F
from .models.categoria import Categoria
from .models.producto import Producto
from .models.proveedor import Proveedor
from .models.movimiento import MovimientoInventario
from .models.almacen import Almacen
from .models.contacto_proveedor import ContactoProveedor
from .models.lote import Lote
from .models.orden_compra import OrdenCompra, ItemOrdenCompra
from .models.stock_almacen import StockAlmacen
from .models.variacion import Variacion
from .models.atributo import Atributo
from .models.valor_atributo import ValorAtributo


class ContactoProveedorInline(admin.TabularInline):
    model = ContactoProveedor
    extra = 1
    fields = ('nombre', 'telefono', 'email', 'cargo')
    autocomplete_fields = ['proveedor']


class ItemOrdenCompraInline(admin.TabularInline):
    model = ItemOrdenCompra
    extra = 1
    fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal')
    readonly_fields = ('subtotal',)
    autocomplete_fields = ['producto']


class VariacionInline(admin.TabularInline):
    model = Variacion
    extra = 1
    fields = ('valor_atributo', 'codigo', 'stock', 'precio_venta', 'imagen')
    autocomplete_fields = ['valor_atributo']


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'ruta_completa', 'codigo', 'categoria_padre', 'orden', 'activo')
    list_filter = ('activo', 'categoria_padre')
    search_fields = ('nombre', 'codigo', 'descripcion')
    list_editable = ('orden',)
    list_select_related = ('categoria_padre',)
    readonly_fields = ('fecha_creacion', 'fecha_modificacion', 'creado_por', 'modificado_por')
    fieldsets = (
        (None, {'fields': ('nombre', 'codigo', 'descripcion', 'imagen', 'categoria_padre', 'orden')}),
        (_('Auditoría'), {'fields': ('activo', 'creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')}),
    )
    actions = ['activar_categorias', 'desactivar_categorias']

    def activar_categorias(self, request, queryset):
        queryset.update(activo=True)
    activar_categorias.short_description = _('Activar categorías seleccionadas')

    def desactivar_categorias(self, request, queryset):
        queryset.update(activo=False)
    desactivar_categorias.short_description = _('Desactivar categorías seleccionadas')


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'categoria', 'precio_venta', 'stock', 'estado', 'disponible', 'activo')
    list_filter = ('categoria', 'estado', 'tipo', 'es_inventariable', 'mostrar_en_tienda', 'destacado', 'activo')
    search_fields = ('codigo', 'nombre', 'descripcion')
    list_editable = ('precio_venta', 'estado')
    list_select_related = ('categoria',)
    readonly_fields = ('fecha_creacion', 'fecha_modificacion', 'creado_por', 'modificado_por',
                      'fecha_ultima_compra', 'fecha_ultimo_movimiento')
    fieldsets = (
        (None, {'fields': ('codigo', 'nombre', 'descripcion', 'categoria', 'imagen')}),
        (_('Precios'), {'fields': ('precio_compra', 'precio_venta', 'iva')}),
        (_('Inventario'), {'fields': ('tipo', 'es_inventariable', 'stock', 'stock_minimo')}),
        (_('Proveedores'), {'fields': ('proveedores',)}),
        (_('Estado'), {'fields': ('estado', 'activo')}),
        (_('E-commerce'), {'fields': ('mostrar_en_tienda', 'destacado', 'url_slug')}),
        (_('Fechas'), {'fields': ('fecha_ultima_compra', 'fecha_ultimo_movimiento')}),
        (_('Auditoría'), {'fields': ('creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')}),
    )
    inlines = [VariacionInline]
    autocomplete_fields = ['categoria', 'proveedores']
    actions = ['marcar_como_destacado', 'quitar_destacado']

    def marcar_como_destacado(self, request, queryset):
        queryset.update(destacado=True)
    marcar_como_destacado.short_description = _('Marcar como destacado')

    def quitar_destacado(self, request, queryset):
        queryset.update(destacado=False)
    quitar_destacado.short_description = _('Quitar destacado')


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'ruc', 'telefono', 'email', 'dias_credito', 'limite_credito', 'estado', 'activo')
    list_filter = ('estado', 'activo')
    search_fields = ('nombre', 'ruc', 'email')
    list_editable = ('dias_credito', 'estado')
    readonly_fields = ('fecha_creacion', 'fecha_modificacion', 'creado_por', 'modificado_por')
    fieldsets = (
        (None, {'fields': ('nombre', 'ruc', 'direccion', 'telefono', 'email', 'sitio_web')}),
        (_('Crédito'), {'fields': ('dias_credito', 'limite_credito')}),
        (_('Información adicional'), {'fields': ('notas',)}),
        (_('Auditoría'), {'fields': ('estado', 'activo', 'creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')}),
    )
    inlines = [ContactoProveedorInline]
    actions = ['activar_proveedores', 'desactivar_proveedores']

    def activar_proveedores(self, request, queryset):
        queryset.update(estado='activo')
    activar_proveedores.short_description = _('Activar proveedores seleccionados')

    def desactivar_proveedores(self, request, queryset):
        queryset.update(estado='inactivo')
    desactivar_proveedores.short_description = _('Desactivar proveedores seleccionados')


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'tipo', 'origen', 'producto', 'cantidad', 'almacen', 'stock_nuevo')
    list_filter = ('tipo', 'origen', 'almacen', 'fecha')
    search_fields = ('producto__nombre', 'producto__codigo', 'documento', 'notas')
    list_select_related = ('producto', 'almacen', 'proveedor', 'lote')
    readonly_fields = ('fecha', 'stock_anterior', 'stock_nuevo', 'fecha_creacion', 'fecha_modificacion', 'creado_por', 'modificado_por')
    fieldsets = (
        (None, {'fields': ('tipo', 'origen', 'producto', 'cantidad', 'stock_anterior', 'stock_nuevo')}),
        (_('Información adicional'), {'fields': ('costo_unitario', 'proveedor', 'almacen', 'lote', 'documento', 'notas')}),
        (_('Trazabilidad'), {'fields': ('referencia_id', 'referencia_tipo')}),
        (_('Auditoría'), {'fields': ('fecha', 'creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')}),
    )
    autocomplete_fields = ['producto', 'proveedor', 'almacen', 'lote']
    date_hierarchy = 'fecha'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('producto', 'almacen', 'proveedor', 'lote')


@admin.register(Almacen)
class AlmacenAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'direccion', 'responsable', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre', 'direccion', 'responsable')
    list_editable = ('responsable',)
    readonly_fields = ('fecha_creacion', 'fecha_modificacion', 'creado_por', 'modificado_por')
    fieldsets = (
        (None, {'fields': ('nombre', 'direccion', 'responsable')}),
        (_('Auditoría'), {'fields': ('activo', 'creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')}),
    )
    actions = ['activar_almacenes', 'desactivar_almacenes']

    def activar_almacenes(self, request, queryset):
        queryset.update(activo=True)
    activar_almacenes.short_description = _('Activar almacenes seleccionados')

    def desactivar_almacenes(self, request, queryset):
        queryset.update(activo=False)
    desactivar_almacenes.short_description = _('Desactivar almacenes seleccionados')


@admin.register(ContactoProveedor)
class ContactoProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'proveedor', 'telefono', 'email', 'cargo')
    list_filter = ('proveedor',)
    search_fields = ('nombre', 'telefono', 'email', 'cargo', 'proveedor__nombre')
    readonly_fields = ('fecha_creacion', 'fecha_modificacion', 'creado_por', 'modificado_por')
    fieldsets = (
        (None, {'fields': ('proveedor', 'nombre', 'telefono', 'email', 'cargo')}),
        (_('Auditoría'), {'fields': ('creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')}),
    )
    autocomplete_fields = ['proveedor']


@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    list_display = ('numero_lote', 'producto', 'almacen', 'cantidad', 'fecha_vencimiento', 'fecha_produccion')
    list_filter = ('producto', 'almacen')
    search_fields = ('numero_lote', 'producto__nombre', 'producto__codigo')
    readonly_fields = ('fecha_creacion', 'fecha_modificacion', 'creado_por', 'modificado_por')
    fieldsets = (
        (None, {'fields': ('producto', 'numero_lote', 'almacen', 'cantidad', 'fecha_produccion', 'fecha_vencimiento')}),
        (_('Auditoría'), {'fields': ('creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')}),
    )
    autocomplete_fields = ['producto', 'almacen']

    class VencimientoFilter(SimpleListFilter):
        title = _('estado de vencimiento')
        parameter_name = 'vencimiento'

        def lookups(self, request, model_admin):
            return (
                ('vigente', _('Vigente')),
                ('vencido', _('Vencido')),
            )

        def queryset(self, request, queryset):
            from django.utils import timezone
            today = timezone.now().date()
            if self.value() == 'vigente':
                return queryset.filter(Q(fecha_vencimiento__gte=today) | Q(fecha_vencimiento__isnull=True))
            if self.value() == 'vencido':
                return queryset.filter(fecha_vencimiento__lt=today)
    list_filter = ('producto', 'almacen', VencimientoFilter)


@admin.register(OrdenCompra)
class OrdenCompraAdmin(admin.ModelAdmin):
    list_display = ('numero', 'proveedor', 'fecha', 'estado', 'total')
    list_filter = ('estado', 'proveedor')
    search_fields = ('numero', 'proveedor__nombre', 'proveedor__ruc')
    list_editable = ('estado',)
    readonly_fields = ('total', 'fecha_creacion', 'fecha_modificacion', 'creado_por', 'modificado_por')
    fieldsets = (
        (None, {'fields': ('numero', 'proveedor', 'fecha', 'estado', 'total')}),
        (_('Auditoría'), {'fields': ('creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')}),
    )
    inlines = [ItemOrdenCompraInline]
    autocomplete_fields = ['proveedor']
    date_hierarchy = 'fecha'
    actions = ['marcar_completada', 'marcar_cancelada']

    def marcar_completada(self, request, queryset):
        queryset.update(estado='completada')
    marcar_completada.short_description = _('Marcar como completada')

    def marcar_cancelada(self, request, queryset):
        queryset.update(estado='cancelada')
    marcar_cancelada.short_description = _('Marcar como cancelada')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('proveedor')


@admin.register(StockAlmacen)
class StockAlmacenAdmin(admin.ModelAdmin):
    list_display = ('producto', 'almacen', 'cantidad')
    list_filter = ('producto', 'almacen')
    search_fields = ('producto__nombre', 'producto__codigo', 'almacen__nombre')
    readonly_fields = ('fecha_creacion', 'fecha_modificacion', 'creado_por', 'modificado_por')
    fieldsets = (
        (None, {'fields': ('producto', 'almacen', 'cantidad')}),
        (_('Auditoría'), {'fields': ('creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')}),
    )
    autocomplete_fields = ['producto', 'almacen']

    class StockBajoFilter(SimpleListFilter):
        title = _('nivel de stock')
        parameter_name = 'stock'

        def lookups(self, request, model_admin):
            return (
                ('bajo', _('Stock bajo')),
                ('adecuado', _('Stock adecuado')),
            )

        def queryset(self, request, queryset):
            if self.value() == 'bajo':
                return queryset.filter(producto__stock_minimo__gt=0, cantidad__lte=F('producto__stock_minimo'))
            if self.value() == 'adecuado':
                return queryset.filter(Q(producto__stock_minimo=0) | Q(cantidad__gt=F('producto__stock_minimo')))
    list_filter = ('producto', 'almacen', StockBajoFilter)


@admin.register(Variacion)
class VariacionAdmin(admin.ModelAdmin):
    list_display = ('producto', 'valor_atributo', 'codigo', 'stock', 'precio_venta')
    list_filter = ('producto', 'valor_atributo__atributo')
    search_fields = ('producto__nombre', 'producto__codigo', 'valor_atributo__valor', 'codigo')
    readonly_fields = ('fecha_creacion', 'fecha_modificacion', 'creado_por', 'modificado_por')
    fieldsets = (
        (None, {'fields': ('producto', 'valor_atributo', 'codigo', 'stock', 'precio_venta', 'imagen')}),
        (_('Auditoría'), {'fields': ('creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')}),
    )
    autocomplete_fields = ['producto', 'valor_atributo']


@admin.register(Atributo)
class AtributoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo')
    list_filter = ('activo', 'categorias')
    search_fields = ('nombre', 'descripcion')
    readonly_fields = ('fecha_creacion', 'fecha_modificacion', 'creado_por', 'modificado_por')
    fieldsets = (
        (None, {'fields': ('nombre', 'descripcion', 'categorias')}),
        (_('Auditoría'), {'fields': ('activo', 'creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')}),
    )
    autocomplete_fields = ['categorias']
    actions = ['activar_atributos', 'desactivar_atributos']

    def activar_atributos(self, request, queryset):
        queryset.update(activo=True)
    activar_atributos.short_description = _('Activar atributos seleccionados')

    def desactivar_atributos(self, request, queryset):
        queryset.update(activo=False)
    desactivar_atributos.short_description = _('Desactivar atributos seleccionados')


@admin.register(ValorAtributo)
class ValorAtributoAdmin(admin.ModelAdmin):
    list_display = ('atributo', 'valor', 'codigo', 'precio_adicional', 'activo')
    list_filter = ('atributo', 'activo')
    search_fields = ('atributo__nombre', 'valor', 'codigo')
    readonly_fields = ('fecha_creacion', 'fecha_modificacion', 'creado_por', 'modificado_por')
    fieldsets = (
        (None, {'fields': ('atributo', 'valor', 'codigo', 'precio_adicional', 'imagen', 'productos')}),
        (_('Auditoría'), {'fields': ('activo', 'creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')}),
    )
    autocomplete_fields = ['atributo', 'productos']
    actions = ['activar_valores', 'desactivar_valores']

    def activar_valores(self, request, queryset):
        queryset.update(activo=True)
    activar_valores.short_description = _('Activar valores seleccionados')

    def desactivar_valores(self, request, queryset):
        queryset.update(activo=False)
    desactivar_valores.short_description = _('Desactivar valores seleccionados')