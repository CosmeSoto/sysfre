from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Categoria, Producto, Proveedor, MovimientoInventario


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'categoria_padre', 'orden', 'activo')
    list_filter = ('activo', 'categoria_padre')
    search_fields = ('nombre', 'codigo', 'descripcion')
    readonly_fields = ('fecha_creacion', 'fecha_modificacion', 'creado_por', 'modificado_por')
    fieldsets = (
        (None, {'fields': ('nombre', 'codigo', 'descripcion', 'imagen', 'categoria_padre', 'orden')}),
        (_('Auditoría'), {'fields': ('activo', 'creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')}),
    )


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'categoria', 'precio_venta', 'stock', 'estado', 'activo')
    list_filter = ('categoria', 'estado', 'tipo', 'es_inventariable', 'mostrar_en_tienda', 'activo')
    search_fields = ('codigo', 'nombre', 'descripcion')
    readonly_fields = ('fecha_creacion', 'fecha_modificacion', 'creado_por', 'modificado_por', 
                      'fecha_ultima_compra', 'fecha_ultimo_movimiento')
    fieldsets = (
        (None, {'fields': ('codigo', 'nombre', 'descripcion', 'categoria', 'imagen')}),
        (_('Precios'), {'fields': ('precio_compra', 'precio_venta', 'iva')}),
        (_('Inventario'), {'fields': ('tipo', 'es_inventariable', 'stock', 'stock_minimo')}),
        (_('Estado'), {'fields': ('estado', 'activo')}),
        (_('E-commerce'), {'fields': ('mostrar_en_tienda', 'destacado', 'url_slug')}),
        (_('Fechas'), {'fields': ('fecha_ultima_compra', 'fecha_ultimo_movimiento')}),
        (_('Auditoría'), {'fields': ('creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')}),
    )


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'ruc', 'telefono', 'email', 'dias_credito', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre', 'ruc', 'email', 'contacto_nombre')
    readonly_fields = ('fecha_creacion', 'fecha_modificacion', 'creado_por', 'modificado_por')
    fieldsets = (
        (None, {'fields': ('nombre', 'ruc', 'direccion', 'telefono', 'email', 'sitio_web')}),
        (_('Contacto'), {'fields': ('contacto_nombre', 'contacto_telefono', 'contacto_email')}),
        (_('Crédito'), {'fields': ('dias_credito', 'limite_credito')}),
        (_('Información adicional'), {'fields': ('notas',)}),
        (_('Auditoría'), {'fields': ('activo', 'creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')}),
    )


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'tipo', 'origen', 'producto', 'cantidad', 'stock_nuevo')
    list_filter = ('tipo', 'origen', 'fecha')
    search_fields = ('producto__nombre', 'producto__codigo', 'documento', 'notas')
    readonly_fields = ('fecha_creacion', 'fecha_modificacion', 'creado_por', 'modificado_por')
    fieldsets = (
        (None, {'fields': ('tipo', 'origen', 'producto', 'cantidad', 'stock_anterior', 'stock_nuevo')}),
        (_('Información adicional'), {'fields': ('costo_unitario', 'proveedor', 'documento', 'notas')}),
        (_('Trazabilidad'), {'fields': ('referencia_id', 'referencia_tipo')}),
        (_('Auditoría'), {'fields': ('creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')}),
    )