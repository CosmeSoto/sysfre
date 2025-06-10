from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import PeriodoFiscal, CuentaContable, AsientoContable, LineaAsiento, Comprobante


class LineaAsientoInline(admin.TabularInline):
    model = LineaAsiento
    extra = 0
    fields = ('cuenta', 'descripcion', 'debe', 'haber')





@admin.register(PeriodoFiscal)
class PeriodoFiscalAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha_inicio', 'fecha_fin', 'estado', 'esta_activo', 'activo')
    list_filter = ('estado', 'activo')
    search_fields = ('nombre', 'notas')
    readonly_fields = ('fecha_creacion', 'fecha_modificacion', 'creado_por', 'modificado_por')
    
    fieldsets = (
        (None, {'fields': ('nombre', 'fecha_inicio', 'fecha_fin', 'estado', 'notas')}),
        (_('Auditoría'), {'fields': ('activo', 'creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')}),
    )


@admin.register(CuentaContable)
class CuentaContableAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'tipo', 'cuenta_padre', 'activo')
    list_filter = ('tipo', 'activo')
    search_fields = ('codigo', 'nombre', 'descripcion')
    readonly_fields = ('fecha_creacion', 'fecha_modificacion', 'creado_por', 'modificado_por')
    
    fieldsets = (
        (None, {'fields': ('codigo', 'nombre', 'tipo', 'cuenta_padre', 'descripcion')}),
        (_('Auditoría'), {'fields': ('activo', 'creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')}),
    )


@admin.register(AsientoContable)
class AsientoContableAdmin(admin.ModelAdmin):
    list_display = ('numero', 'fecha', 'periodo_fiscal', 'tipo', 'concepto', 'estado', 'total_debe', 'total_haber', 'esta_balanceado')
    list_filter = ('estado', 'tipo', 'periodo_fiscal', 'fecha')
    search_fields = ('numero', 'concepto', 'notas')
    readonly_fields = ('fecha_creacion', 'fecha_modificacion', 'creado_por', 'modificado_por')
    inlines = [LineaAsientoInline]
    
    fieldsets = (
        (None, {'fields': ('numero', 'fecha', 'periodo_fiscal', 'tipo', 'concepto', 'estado')}),
        (_('Información adicional'), {'fields': ('notas',)}),
        (_('Trazabilidad'), {'fields': ('referencia_id', 'referencia_tipo')}),
        (_('Auditoría'), {'fields': ('activo', 'creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')}),
    )


@admin.register(LineaAsiento)
class LineaAsientoAdmin(admin.ModelAdmin):
    list_display = ('asiento', 'cuenta', 'descripcion', 'debe', 'haber')
    list_filter = ('asiento__estado',)
    search_fields = ('descripcion', 'cuenta__nombre', 'cuenta__codigo', 'asiento__numero')
    readonly_fields = ('fecha_creacion', 'fecha_modificacion', 'creado_por', 'modificado_por')
    
    fieldsets = (
        (None, {'fields': ('asiento', 'cuenta', 'descripcion', 'debe', 'haber')}),
        (_('Auditoría'), {'fields': ('activo', 'creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')}),
    )


@admin.register(Comprobante)
class ComprobanteAdmin(admin.ModelAdmin):
    list_display = ('numero', 'tipo', 'fecha_emision', 'proveedor', 'total', 'estado')
    list_filter = ('tipo', 'estado', 'fecha_emision')
    search_fields = ('numero', 'proveedor__nombre', 'proveedor__ruc')
    readonly_fields = ('fecha_creacion', 'fecha_modificacion', 'creado_por', 'modificado_por')
    
    fieldsets = (
        (None, {'fields': ('numero', 'tipo', 'fecha_emision', 'proveedor', 'estado')}),
        (_('Valores'), {'fields': ('subtotal', 'impuestos', 'total')}),
        (_('Documentos relacionados'), {'fields': ('comprobante_relacionado', 'asiento_contable')}),
        (_('Auditoría'), {'fields': ('activo', 'creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')}),
    )