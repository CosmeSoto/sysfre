from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.contrib.admin.widgets import AdminSplitDateTime
from django.db import models
from django.utils import timezone
from .models import Venta, DetalleVenta, Pago, Envio, NotaCredito, DetalleNotaCredito
from .services.venta_service import VentaService
import logging

# Configurar logger
logger = logging.getLogger('sysfree')

# Inlines
class DetalleVentaInline(admin.TabularInline):
    """Inline para detalles de venta."""
    model = DetalleVenta
    extra = 1
    fields = ('producto', 'cantidad', 'precio_unitario', 'descuento', 'tipo_iva', 'subtotal', 'iva', 'total')
    readonly_fields = ('subtotal', 'iva', 'total')
    autocomplete_fields = ['producto']

class PagoInline(admin.TabularInline):
    """Inline para pagos."""
    model = Pago
    extra = 0
    fields = ('metodo', 'monto', 'referencia', 'estado', 'numero_tarjeta', 'banco')
    readonly_fields = ('fecha',)
    autocomplete_fields = ['venta']

class EnvioInline(admin.TabularInline):
    """Inline para envíos."""
    model = Envio
    extra = 0
    fields = ('transportista', 'numero_seguimiento', 'estado', 'fecha_envio', 'fecha_entrega', 'notas')
    readonly_fields = ('fecha_entrega',)
    autocomplete_fields = ['venta']

class DetalleNotaCreditoInline(admin.TabularInline):
    """Inline para detalles de nota de crédito."""
    model = DetalleNotaCredito
    extra = 1
    fields = ('producto', 'cantidad', 'precio_unitario', 'tipo_iva', 'subtotal', 'iva', 'total')
    readonly_fields = ('subtotal', 'iva', 'total')
    autocomplete_fields = ['producto']

# Admin classes
@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    """Admin para ventas y proformas."""
    list_display = (
        'numero', 'fecha', 'cliente', 'tipo', 'estado', 'reparacion_numero',
        'total', 'esta_pagado', 'esta_vencida'
    )
    list_filter = ('estado', 'tipo', 'fecha', 'reparacion', 'cliente')
    search_fields = (
        'numero', 'cliente__nombres', 'cliente__apellidos', 'cliente__email',
        'reparacion__numero', 'clave_acceso'
    )
    readonly_fields = (
        'fecha', 'numero', 'subtotal', 'total', 'iva', 'fecha_creacion',
        'fecha_modificacion', 'creado_por', 'modificado_por'
    )
    inlines = [DetalleVentaInline, PagoInline, EnvioInline]
    date_hierarchy = 'fecha'
    formfield_overrides = {
        models.DateTimeField: {'widget': AdminSplitDateTime},
    }
    fieldsets = (
        (None, {'fields': ('numero', 'fecha', 'cliente', 'tipo', 'estado')}),
        (_('Direcciones'), {'fields': ('direccion_facturacion', 'direccion_envio')}),
        (_('Totales'), {'fields': ('subtotal', 'descuento', 'tipo_iva', 'iva', 'total')}),
        (_('Referencias'), {'fields': ('reparacion', 'venta_relacionada')}),
        (_('Facturación electrónica'), {'fields': ('clave_acceso', 'numero_autorizacion', 'fecha_autorizacion')}),
        (_('Fechas'), {'fields': ('fecha_pago', 'fecha_envio', 'fecha_entrega', 'validez')}),
        (_('Notas'), {'fields': ('notas',)}),
        (_('Auditoría'), {'fields': ('activo', 'creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')}),
    )
    ordering = ('-fecha', '-numero')
    autocomplete_fields = [
        'cliente', 'reparacion', 'venta_relacionada', 'tipo_iva',
        'direccion_facturacion', 'direccion_envio'
    ]

    def reparacion_numero(self, obj):
        """Muestra el número de la reparación asociada."""
        return obj.reparacion.numero if obj.reparacion else _('Sin reparación')
    reparacion_numero.short_description = _('Reparación')

    def esta_pagado(self, obj):
        """Muestra si la venta está pagada."""
        return obj.esta_pagado
    esta_pagado.short_description = _('Pagado')
    esta_pagado.boolean = True

    def esta_vencida(self, obj):
        """Muestra si la proforma está vencida."""
        return obj.esta_vencida
    esta_vencida.short_description = _('Vencida')
    esta_vencida.boolean = True

    def convertir_a_factura(self, request, queryset):
        """Convierte proformas seleccionadas a facturas."""
        try:
            for proforma in queryset.filter(tipo='proforma', estado='aceptada'):
                if proforma.esta_vencida:
                    self.message_user(
                        request,
                        _(f"La proforma {proforma.numero} está vencida y no puede ser convertida"),
                        level=messages.WARNING
                    )
                    continue
                factura = VentaService.convertir_proforma_a_factura(
                    proforma,
                    usuario=request.user
                )
                logger.info(f"Proforma {proforma.numero} convertida a factura {factura.numero} por {request.user}")
            self.message_user(request, _("Proformas convertidas con éxito"))
        except Exception as e:
            logger.error(f"Error al convertir proforma: {str(e)}")
            self.message_user(request, _(f"Error: {str(e)}"), level=messages.ERROR)
    convertir_a_factura.short_description = _('Convertir a factura')

    def marcar_como_pagada(self, request, queryset):
        """Marca las ventas seleccionadas como pagadas."""
        try:
            for venta in queryset.filter(estado__in=['borrador', 'emitida']):
                venta.estado = 'pagada'
                venta.fecha_pago = timezone.now()
                venta.modificado_por = request.user
                venta.save()
                logger.info(f"Venta {venta.numero} marcada como pagada por {request.user}")
            self.message_user(request, _("Ventas marcadas como pagadas con éxito"))
        except Exception as e:
            logger.error(f"Error al marcar como pagada: {str(e)}")
            self.message_user(request, _(f"Error: {str(e)}"), level=messages.ERROR)
    marcar_como_pagada.short_description = _('Marcar como pagada')

    actions = ['convertir_a_factura', 'marcar_como_pagada']

@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    """Admin para detalles de venta."""
    list_display = ('venta', 'producto', 'cantidad', 'precio_unitario', 'descuento', 'subtotal', 'iva', 'total')
    list_filter = ('venta__tipo', 'venta__estado')
    search_fields = ('venta__numero', 'producto__nombre')
    readonly_fields = (
        'subtotal', 'iva', 'total', 'fecha_creacion', 'fecha_modificacion',
        'creado_por', 'modificado_por'
    )
    fieldsets = (
        (None, {'fields': ('venta', 'producto', 'cantidad', 'precio_unitario', 'descuento', 'tipo_iva')}),
        (_('Totales'), {'fields': ('subtotal', 'iva', 'total')}),
        (_('Auditoría'), {'fields': ('activo', 'creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')}),
    )
    autocomplete_fields = ['venta', 'producto', 'tipo_iva']

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    """Admin para pagos."""
    list_display = ('venta', 'fecha', 'metodo', 'monto', 'estado', 'referencia')
    list_filter = ('metodo', 'estado', 'fecha')
    search_fields = ('venta__numero', 'referencia', 'notas')
    readonly_fields = (
        'fecha', 'fecha_creacion', 'fecha_modificacion', 'creado_por', 'modificado_por'
    )
    formfield_overrides = {
        models.DateTimeField: {'widget': AdminSplitDateTime},
    }
    fieldsets = (
        (None, {'fields': ('venta', 'metodo', 'monto', 'referencia', 'estado')}),
        (_('Detalles de pago'), {
            'fields': ('numero_tarjeta', 'titular_tarjeta', 'banco', 'numero_cuenta', 'numero_cheque', 'banco_cheque'),
            'classes': ('collapse',),
        }),
        (_('Notas'), {'fields': ('notas',)}),
        (_('Auditoría'), {'fields': ('activo', 'creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')}),
    )
    autocomplete_fields = ['venta']

@admin.register(Envio)
class EnvioAdmin(admin.ModelAdmin):
    """Admin para envíos."""
    list_display = ('venta', 'transportista', 'numero_seguimiento', 'estado', 'fecha_envio')
    list_filter = ('estado', 'fecha_envio')
    search_fields = ('venta__numero', 'transportista', 'numero_seguimiento')
    readonly_fields = ('fecha_creacion', 'fecha_modificacion', 'creado_por', 'modificado_por')
    date_hierarchy = 'fecha_envio'
    fieldsets = (
        (None, {'fields': ('venta', 'transportista', 'numero_seguimiento', 'estado')}),
        (_('Fechas'), {'fields': ('fecha_envio', 'fecha_entrega')}),
        (_('Notas'), {'fields': ('notas',)}),
        (_('Auditoría'), {'fields': ('activo', 'creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')}),
    )
    autocomplete_fields = ['venta']

    def marcar_como_entregado(self, request, queryset):
        """Marca los envíos seleccionados como entregados."""
        try:
            for envio in queryset.filter(estado__in=['pendiente', 'en_transito']):
                envio.estado = 'entregado'
                envio.fecha_entrega = timezone.now()
                envio.modificado_por = request.user
                envio.save()
                logger.info(f"Envío {envio.numero_seguimiento} marcado como entregado por {request.user}")
            self.message_user(request, _("Envíos marcados como entregados con éxito"))
        except Exception as e:
            logger.error(f"Error al marcar como entregado: {str(e)}")
            self.message_user(request, _(f"Error: {str(e)}"), level=messages.ERROR)
    marcar_como_entregado.short_description = _('Marcar como entregado')

    actions = ['marcar_como_entregado']

@admin.register(NotaCredito)
class NotaCreditoAdmin(admin.ModelAdmin):
    """Admin para notas de crédito."""
    list_display = ('numero', 'fecha', 'venta', 'cliente', 'estado', 'total')
    list_filter = ('estado', 'fecha', 'cliente')
    search_fields = (
        'numero', 'venta__numero', 'cliente__nombres', 'cliente__apellidos', 'cliente__email'
    )
    readonly_fields = (
        'fecha', 'subtotal', 'total', 'iva', 'fecha_creacion', 'fecha_modificacion',
        'creado_por', 'modificado_por'
    )
    inlines = [DetalleNotaCreditoInline]
    date_hierarchy = 'fecha'
    formfield_overrides = {
        models.DateTimeField: {'widget': AdminSplitDateTime},
    }
    fieldsets = (
        (None, {'fields': ('numero', 'fecha', 'venta', 'cliente', 'estado')}),
        (_('Detalles'), {'fields': ('motivo', 'subtotal', 'tipo_iva', 'iva', 'total')}),
        (_('Auditoría'), {'fields': ('activo', 'creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')}),
    )
    autocomplete_fields = ['nota_credito', 'producto', 'tipo_iva']
    ordering = ('-fecha', '-numero')
    autocomplete_fields = ['venta', 'cliente', 'tipo_iva']

    def emitir_nota_credito(self, request, queryset):
        """Emite las notas de crédito seleccionadas."""
        try:
            for nota in queryset.filter(estado='borrador'):
                nota.estado = 'emitida'
                nota.modificado_por = request.user
                nota.save()
                logger.info(f"Nota de crédito {nota.numero} emitida por {request.user}")
            self.message_user(request, _("Notas de crédito emitidas con éxito"))
        except Exception as e:
            logger.error(f"Error al emitir nota de crédito: {str(e)}")
            self.message_user(request, _(f"Error: {str(e)}"), level=messages.ERROR)
    emitir_nota_credito.short_description = _('Emitir nota de crédito')

    actions = ['emitir_nota_credito']

@admin.register(DetalleNotaCredito)
class DetalleNotaCreditoAdmin(admin.ModelAdmin):
    """Admin para detalles de nota de crédito."""
    list_display = ('nota_credito', 'producto', 'cantidad', 'precio_unitario', 'subtotal', 'iva', 'total')
    list_filter = ('nota_credito__estado', 'nota_credito__cliente')
    search_fields = ('nota_credito__numero', 'producto__nombre')
    readonly_fields = (
        'subtotal', 'iva', 'total', 'fecha_creacion', 'fecha_modificacion',
        'creado_por', 'modificado_por'
    )
    fieldsets = (
        (None, {'fields': ('nota_credito', 'producto', 'cantidad', 'precio_unitario', 'tipo_iva')}),
        (_('Totales'), {'fields': ('subtotal', 'iva', 'total')}),
        (_('Auditoría'), {'fields': ('activo', 'creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')}),
    )