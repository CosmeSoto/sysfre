from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.utils import timezone
from .models import Reparacion, SeguimientoReparacion, RepuestoReparacion, ServicioReparacion, CitaServicio, GarantiaReparacion
from .services.reparacion_service import ReparacionService
from .services.venta_service import ReparacionVentaService
import logging
from haystack.query import SearchQuerySet
from inventario.services.inventario_service import InventarioService
from inventario.models import Almacen

# Configurar logger
logger = logging.getLogger('sysfree')

class SeguimientoReparacionInline(admin.TabularInline):
    """Inline para gestionar seguimientos de reparación."""
    model = SeguimientoReparacion
    extra = 1
    fields = ('estado_anterior', 'estado_nuevo', 'comentario', 'notificado_cliente', 'metodo_notificacion')
    readonly_fields = ('fecha',)

class RepuestoReparacionInline(admin.TabularInline):
    """Inline para gestionar repuestos usados en reparación."""
    model = RepuestoReparacion
    extra = 1
    fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal')
    readonly_fields = ('subtotal',)

@admin.register(ServicioReparacion)
class ServicioReparacionAdmin(admin.ModelAdmin):
    """Admin para servicios de reparación."""
    list_display = ('nombre', 'tipo', 'precio', 'tiempo_estimado', 'disponible_online', 'producto_categoria', 'reparaciones_count')
    list_filter = ('tipo', 'disponible_online', 'producto__categoria')
    search_fields = ('nombre', 'descripcion', 'producto__nombre')
    readonly_fields = ('fecha_creacion', 'fecha_modificacion', 'creado_por', 'modificado_por')
    fieldsets = (
        (None, {'fields': ('nombre', 'descripcion', 'tipo', 'precio', 'tiempo_estimado')}),
        (_('Configuración'), {'fields': ('producto', 'requiere_diagnostico_previo', 'disponible_online')}),
        (_('Auditoría'), {'fields': ('activo', 'creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')}),
    )

    def producto_categoria(self, obj):
        """Muestra la categoría del producto asociado."""
        return obj.producto.categoria if obj.producto else _('Sin producto')
    producto_categoria.short_description = _('Categoría')

    def reparaciones_count(self, obj):
        """Muestra el número de reparaciones asociadas."""
        return obj.reparaciones.count()
    reparaciones_count.short_description = _('Reparaciones')

@admin.register(Reparacion)
class ReparacionAdmin(admin.ModelAdmin):
    """Admin para reparaciones con búsqueda avanzada y acciones avanzadas."""
    list_display = (
        'numero', 'cliente', 'tipo_equipo', 'estado', 'prioridad',
        'fecha_recepcion', 'tecnico', 'facturado', 'numero_factura', 'ultima_notificacion'
    )
    list_filter = ('estado', 'prioridad', 'tecnico', 'fecha_recepcion', 'facturado', 'factura__tipo')
    search_fields = (
        'numero', 'cliente__nombres', 'cliente__apellidos', 'cliente__email',
        'tipo_equipo', 'marca', 'modelo', 'factura__numero'
    )
    readonly_fields = (
        'numero', 'total', 'fecha_recepcion', 'fecha_creacion', 'fecha_modificacion',
        'creado_por', 'modificado_por'
    )
    inlines = (SeguimientoReparacionInline, RepuestoReparacionInline)
    date_hierarchy = 'fecha_recepcion'
    fieldsets = (
        (None, {'fields': ('numero', 'cliente', 'fecha_estimada_entrega', 'fecha_entrega')}),
        (_('Información del equipo'), {'fields': ('tipo_equipo', 'marca', 'modelo')}),
        (_('Detalles de la reparación'), {'fields': ('problema_reportado',)}),
        (_('Estado y seguimiento'), {'fields': ('estado', 'prioridad', 'tecnico')}),
        (_('Costos'), {'fields': ('costo_diagnostico', 'costo_reparacion', 'costo_repuestos', 'total')}),
        (_('Facturación'), {'fields': ('facturado', 'factura')}),
        (_('Auditoría'), {'fields': ('activo', 'creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')}),
    )

    def numero_factura(self, obj):
        """Muestra el número de la factura/proforma asociada."""
        return obj.factura.numero if obj.factura else _('Sin factura')
    numero_factura.short_description = _('Factura')

    def ultima_notificacion(self, obj):
        """Muestra el método de la última notificación."""
        ultimo_seguimiento = obj.seguimientos.filter(notificado_cliente=True).order_by('-fecha').first()
        return ultimo_seguimiento.metodo_notificacion if ultimo_seguimiento else _('No notificado')
    ultima_notificacion.short_description = _('Última notificación')

    def get_search_results(self, request, queryset, search_term):
        """Integra búsqueda avanzada con Haystack."""
        if search_term:
            search_query = SearchQuerySet().models(Reparacion).filter(content=search_term)
            pks = [result.pk for result in search_query]
            queryset = queryset.filter(pk__in=pks)
        return queryset, False

    def cambiar_estado_a_finalizado(self, request, queryset):
        """Cambia el estado de las reparaciones a 'finalizado'."""
        try:
            for reparacion in queryset:
                ReparacionService.cambiar_estado(
                    reparacion,
                    'finalizado',
                    comentario=_('Cambio desde admin'),
                    usuario=request.user
                )
                logger.info(f"Reparación {reparacion.numero} finalizada por {request.user}")
            self.message_user(request, _("Reparaciones finalizadas con éxito"))
        except Exception as e:
            logger.error(f"Error al cambiar estado: {str(e)}")
            self.message_user(request, _(f"Error: {str(e)}"), level=messages.ERROR)
    cambiar_estado_a_finalizado.short_description = _('Cambiar a finalizado')

    def generar_proforma(self, request, queryset):
        """Genera una proforma para las reparaciones seleccionadas."""
        try:
            for reparacion in queryset.filter(factura__isnull=True):
                proforma = ReparacionVentaService.crear_proforma_reparacion(
                    reparacion,
                    usuario=request.user
                )
                logger.info(f"Proforma {proforma.numero} creada para reparación {reparacion.numero}")
            self.message_user(request, _("Proformas generadas con éxito"))
        except Exception as e:
            logger.error(f"Error al generar proforma: {str(e)}")
            self.message_user(request, _(f"Error: {str(e)}"), level=messages.ERROR)
    generar_proforma.short_description = _('Generar proforma')

    def convertir_proforma_a_factura(self, request, queryset):
        """Convierte proformas asociadas a facturas."""
        try:
            from ventas.services.venta_service import VentaService
            for reparacion in queryset.filter(factura__tipo='proforma'):
                factura = VentaService.convertir_proforma_a_factura(
                    reparacion.factura,
                    usuario=request.user
                )
                logger.info(f"Proforma {reparacion.factura.numero} convertida a factura {factura.numero}")
            self.message_user(request, _("Proformas convertidas con éxito"))
        except Exception as e:
            logger.error(f"Error al convertir proforma: {str(e)}")
            self.message_user(request, _(f"Error: {str(e)}"), level=messages.ERROR)
    convertir_proforma_a_factura.short_description = _('Convertir proforma a factura')

    actions = ['cambiar_estado_a_finalizado', 'generar_proforma', 'convertir_proforma_a_factura']

@admin.register(SeguimientoReparacion)
class SeguimientoReparacionAdmin(admin.ModelAdmin):
    """Admin para seguimientos de reparación."""
    list_display = ('reparacion', 'fecha', 'estado_anterior', 'estado_nuevo', 'notificado_cliente', 'metodo_notificacion')
    list_filter = ('estado_nuevo', 'notificado_cliente', 'metodo_notificacion', 'fecha')
    search_fields = ('reparacion__numero', 'comentario')
    readonly_fields = ('fecha', 'fecha_creacion', 'fecha_modificacion', 'creado_por', 'modificado_por')
    date_hierarchy = 'fecha'
    fieldsets = (
        (None, {'fields': ('reparacion', 'estado_anterior', 'estado_nuevo', 'comentario')}),
        (_('Notificación'), {'fields': ('notificado_cliente', 'metodo_notificacion', 'fecha_notificacion')}),
        (_('Auditoría'), {'fields': ('activo', 'creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')}),
    )

    def notificar_cliente(self, request, queryset):
        """Notifica al cliente sobre los seguimientos seleccionados."""
        try:
            for seguimiento in queryset.filter(notificado_cliente=False):
                seguimiento.notificado_cliente = True
                seguimiento.fecha_notificacion = timezone.now()
                seguimiento.metodo_notificacion = 'email'  # Configurable
                seguimiento.save()
                logger.info(f"Notificación enviada para seguimiento de reparación {seguimiento.reparacion.numero}")
            self.message_user(request, _("Notificaciones enviadas con éxito"))
        except Exception as e:
            logger.error(f"Error al notificar cliente: {str(e)}")
            self.message_user(request, _(f"Error: {str(e)}"), level=messages.ERROR)
    notificar_cliente.short_description = _('Notificar cliente')

    actions = ['notificar_cliente']

@admin.register(RepuestoReparacion)
class RepuestoReparacionAdmin(admin.ModelAdmin):
    """Admin para repuestos usados en reparaciones."""
    list_display = ('reparacion', 'producto', 'producto_categoria', 'cantidad', 'precio_unitario', 'subtotal', 'stock_disponible')
    list_filter = ('reparacion__estado', 'producto__categoria')
    search_fields = ('reparacion__numero', 'producto__nombre')
    readonly_fields = ('subtotal', 'fecha_creacion', 'fecha_modificacion', 'creado_por', 'modificado_por')
    fieldsets = (
        (None, {'fields': ('reparacion', 'producto', 'cantidad', 'precio_unitario', 'subtotal')}),
        (_('Auditoría'), {'fields': ('activo', 'creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')}),
    )

    def producto_categoria(self, obj):
        """Muestra la categoría del producto."""
        return obj.producto.categoria if obj.producto else _('Sin producto')
    producto_categoria.short_description = _('Categoría')

    def stock_disponible(self, obj):
        """Muestra el stock disponible del producto."""
        return obj.producto.stock if getattr(obj.producto, 'es_inventariable', False) else 'N/A'
    stock_disponible.short_description = _('Stock')

    def registrar_salida_inventario(self, request, queryset):
        """Registra una salida de inventario para los repuestos seleccionados."""
        try:
            almacen = Almacen.objects.filter(activo=True).first()
            if not almacen:
                raise ValueError(_("No hay almacenes activos disponibles"))
            for repuesto in queryset.filter(producto__es_inventariable=True):
                InventarioService.registrar_salida(
                    producto=repuesto.producto,
                    cantidad=repuesto.cantidad,
                    origen='reparacion',
                    documento=repuesto.reparacion.numero,
                    usuario=request.user,
                    almacen=almacen,
                    referencia_id=repuesto.reparacion.id,
                    referencia_tipo='reparacion'
                )
                logger.info(f"Salida registrada para repuesto {repuesto.producto} en reparación {repuesto.reparacion.numero}")
            self.message_user(request, _("Salidas de inventario registradas con éxito"))
        except Exception as e:
            logger.error(f"Error al registrar salida: {str(e)}")
            self.message_user(request, _(f"Error: {str(e)}"), level=messages.ERROR)
    registrar_salida_inventario.short_description = _('Registrar salida de inventario')

    actions = ['registrar_salida_inventario']

@admin.register(CitaServicio)
class CitaServicioAdmin(admin.ModelAdmin):
    """Admin para citas de servicio."""
    list_display = ('cliente', 'fecha_hora', 'tipo_equipo', 'estado', 'reparacion')
    list_filter = ('estado', 'fecha_hora')
    search_fields = ('cliente__nombres', 'cliente__apellidos', 'cliente__email', 'tipo_equipo', 'reparacion__numero')
    readonly_fields = ('fecha_creacion', 'fecha_modificacion', 'creado_por', 'modificado_por')
    date_hierarchy = 'fecha_hora'
    fieldsets = (
        (None, {'fields': ('cliente', 'fecha_hora', 'tipo_equipo', 'estado', 'reparacion')}),
        (_('Auditoría'), {'fields': ('activo', 'creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')}),
    )

@admin.register(GarantiaReparacion)
class GarantiaReparacionAdmin(admin.ModelAdmin):
    """Admin para garantías de reparación."""
    list_display = ('reparacion', 'fecha_inicio', 'fecha_fin')
    list_filter = ('fecha_inicio', 'fecha_fin')
    search_fields = ('reparacion__numero', 'condiciones')
    readonly_fields = ('fecha_creacion', 'fecha_modificacion', 'creado_por', 'modificado_por')
    fieldsets = (
        (None, {'fields': ('reparacion', 'fecha_inicio', 'fecha_fin', 'condiciones')}),
        (_('Auditoría'), {'fields': ('activo', 'creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')}),
    )