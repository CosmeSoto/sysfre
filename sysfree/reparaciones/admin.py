from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Reparacion, SeguimientoReparacion, RepuestoReparacion, ServicioReparacion


@admin.register(ServicioReparacion)
class ServicioReparacionAdmin(admin.ModelAdmin):
    """Admin para servicios de reparación."""
    list_display = ('nombre', 'tipo', 'precio', 'tiempo_estimado', 'disponible_online')
    list_filter = ('tipo', 'disponible_online')
    search_fields = ('nombre', 'descripcion')
    fieldsets = (
        (None, {
            'fields': ('nombre', 'descripcion', 'tipo', 'precio', 'tiempo_estimado')
        }),
        (_('Configuración'), {
            'fields': ('producto', 'requiere_diagnostico_previo', 'disponible_online')
        }),
    )


class SeguimientoReparacionInline(admin.TabularInline):
    """Inline para seguimientos de reparación."""
    model = SeguimientoReparacion
    extra = 1


class RepuestoReparacionInline(admin.TabularInline):
    """Inline para repuestos usados en reparación."""
    model = RepuestoReparacion
    extra = 1


@admin.register(Reparacion)
class ReparacionAdmin(admin.ModelAdmin):
    """Admin para reparaciones."""
    list_display = ('numero', 'cliente', 'tipo_equipo', 'estado', 'fecha_recepcion', 'tecnico')
    list_filter = ('estado', 'fecha_recepcion')
    search_fields = ('numero', 'cliente__nombre', 'cliente__email', 'tipo_equipo', 'marca', 'modelo')
    date_hierarchy = 'fecha_recepcion'
    inlines = [SeguimientoReparacionInline, RepuestoReparacionInline]
    fieldsets = (
        (None, {
            'fields': ('numero', 'cliente', 'fecha_estimada_entrega')
        }),
        (_('Información del equipo'), {
            'fields': ('tipo_equipo', 'marca', 'modelo', 'numero_serie')
        }),
        (_('Detalles de la reparación'), {
            'fields': ('problema', 'diagnostico', 'solucion')
        }),
        (_('Estado y seguimiento'), {
            'fields': ('estado', 'tecnico')
        }),
        (_('Costos'), {
            'fields': ('costo_estimado', 'total')
        }),
    )
    readonly_fields = ('total', 'fecha_recepcion')


@admin.register(SeguimientoReparacion)
class SeguimientoReparacionAdmin(admin.ModelAdmin):
    """Admin para seguimientos de reparación."""
    list_display = ('reparacion', 'fecha', 'estado_nuevo', 'comentario')
    list_filter = ('estado_nuevo', 'fecha')
    search_fields = ('reparacion__numero', 'descripcion')
    date_hierarchy = 'fecha'


@admin.register(RepuestoReparacion)
class RepuestoReparacionAdmin(admin.ModelAdmin):
    """Admin para repuestos usados en reparación."""
    list_display = ('reparacion', 'producto', 'cantidad', 'precio_unitario', 'subtotal')
    list_filter = ('reparacion__estado',)
    search_fields = ('reparacion__numero', 'producto__nombre')
    readonly_fields = ('subtotal',)