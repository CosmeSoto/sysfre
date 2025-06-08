from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Venta, DetalleVenta, Pago, NotaCredito, DetalleNotaCredito, Envio


class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0
    fields = ('producto', 'cantidad', 'precio_unitario', 'descuento', 'iva', 'subtotal', 'total')
    readonly_fields = ('subtotal', 'total')


class PagoInline(admin.TabularInline):
    model = Pago
    extra = 0
    fields = ('metodo', 'monto', 'referencia', 'estado')
    readonly_fields = ('fecha',)


class DetalleNotaCreditoInline(admin.TabularInline):
    model = DetalleNotaCredito
    extra = 0
    fields = ('producto', 'cantidad', 'precio_unitario', 'iva', 'subtotal', 'total')
    readonly_fields = ('subtotal', 'total')


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'fecha', 'cliente', 'tipo', 'estado', 'total', 'esta_pagado')
    list_filter = ('estado', 'tipo', 'fecha')
    search_fields = ('numero', 'cliente__nombres', 'cliente__apellidos', 'cliente__nombre_comercial', 'cliente__identificacion')
    readonly_fields = ('fecha', 'fecha_creacion', 'fecha_modificacion', 'creado_por', 'modificado_por')
    inlines = [DetalleVentaInline, PagoInline]
    
    def get_fieldsets(self, request, obj=None):
        common_fields = [
            (None, {'fields': ('numero', 'cliente', 'tipo', 'estado')}),
            (_('Direcciones'), {'fields': ('direccion_facturacion', 'direccion_envio')}),
            (_('Totales'), {'fields': ('subtotal', 'iva', 'descuento', 'total')}),
            (_('Información adicional'), {'fields': ('notas',)}),
            (_('Auditoría'), {'fields': ('activo', 'creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')}),
        ]
        
        if obj and obj.tipo == 'proforma':
            proforma_fields = [
                (_('Proforma'), {'fields': ('validez', 'reparacion', 'venta_relacionada')}),
            ]
            return common_fields[:2] + proforma_fields + common_fields[2:]
        else:
            factura_fields = [
                (_('Facturación electrónica'), {'fields': ('clave_acceso', 'numero_autorizacion', 'fecha_autorizacion')}),
                (_('Fechas de seguimiento'), {'fields': ('fecha_pago', 'fecha_envio', 'fecha_entrega')}),
                (_('Referencias'), {'fields': ('reparacion', 'venta_relacionada')}),
            ]
            return common_fields[:3] + factura_fields + common_fields[3:]
    
    def get_list_display(self, request):
        if request.GET.get('tipo') == 'proforma':
            return ('numero', 'fecha', 'cliente', 'estado', 'total', 'esta_vencida')
        return self.list_display


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('venta', 'fecha', 'metodo', 'monto', 'estado')
    list_filter = ('metodo', 'estado', 'fecha')
    search_fields = ('venta__numero', 'referencia', 'notas')
    readonly_fields = ('fecha', 'fecha_creacion', 'fecha_modificacion', 'creado_por', 'modificado_por')
    
    fieldsets = (
        (None, {'fields': ('venta', 'metodo', 'monto', 'referencia', 'estado')}),
        (_('Detalles de pago'), {
            'fields': (
                'numero_tarjeta', 'titular_tarjeta',
                'banco', 'numero_cuenta',
                'numero_cheque', 'banco_cheque'
            ),
            'classes': ('collapse',),
        }),
        (_('Información adicional'), {'fields': ('notas',)}),
        (_('Auditoría'), {'fields': ('activo', 'creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')}),
    )


@admin.register(NotaCredito)
class NotaCreditoAdmin(admin.ModelAdmin):
    list_display = ('numero', 'fecha', 'venta', 'cliente', 'estado', 'total')
    list_filter = ('estado', 'fecha')
    search_fields = ('numero', 'venta__numero', 'cliente__nombres', 'cliente__apellidos', 'cliente__identificacion')
    readonly_fields = ('fecha', 'fecha_creacion', 'fecha_modificacion', 'creado_por', 'modificado_por')
    inlines = [DetalleNotaCreditoInline]
    
    fieldsets = (
        (None, {'fields': ('numero', 'venta', 'cliente', 'estado')}),
        (_('Detalles'), {'fields': ('motivo', 'subtotal', 'iva', 'total')}),
        (_('Auditoría'), {'fields': ('activo', 'creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')}),
    )


@admin.register(Envio)
class EnvioAdmin(admin.ModelAdmin):
    list_display = ('venta', 'transportista', 'numero_seguimiento', 'estado', 'fecha_envio')
    list_filter = ('estado', 'fecha_envio')
    search_fields = ('venta__numero', 'numero_seguimiento', 'transportista')
    readonly_fields = ('fecha_creacion', 'fecha_modificacion', 'creado_por', 'modificado_por')
    
    fieldsets = (
        (None, {'fields': ('venta', 'transportista', 'numero_seguimiento', 'estado')}),
        (_('Fechas'), {'fields': ('fecha_envio', 'fecha_entrega')}),
        (_('Información adicional'), {'fields': ('notas',)}),
        (_('Auditoría'), {'fields': ('activo', 'creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')}),
    )