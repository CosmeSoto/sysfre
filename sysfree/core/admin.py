from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Usuario, ConfiguracionSistema


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('email', 'nombres', 'apellidos', 'is_active', 'is_staff', 'fecha_creacion')
    list_filter = ('is_active', 'is_staff')
    search_fields = ('email', 'nombres', 'apellidos')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Información personal'), {'fields': ('nombres', 'apellidos', 'telefono', 'foto')}),
        (_('Permisos'), {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        (_('Fechas importantes'), {'fields': ('fecha_creacion', 'ultimo_login')}),
    )
    readonly_fields = ('fecha_creacion', 'ultimo_login')


@admin.register(ConfiguracionSistema)
class ConfiguracionSistemaAdmin(admin.ModelAdmin):
    list_display = ('NOMBRE_EMPRESA',)
    fieldsets = (
        (_('Información de la empresa'), {
            'fields': ('NOMBRE_EMPRESA', 'RUC', 'DIRECCION', 'TELEFONO', 'EMAIL', 'SITIO_WEB')
        }),
        (_('Numeración de documentos'), {
            'fields': (
                ('PREFIJO_FACTURA', 'INICIO_FACTURA'),
                ('PREFIJO_PROFORMA', 'INICIO_PROFORMA'),
                ('PREFIJO_NOTA_VENTA', 'INICIO_NOTA_VENTA'),
                ('PREFIJO_TICKET', 'INICIO_TICKET'),
            )
        }),
        (_('Impuestos'), {
            'fields': ('IVA_PORCENTAJE',)
        }),
        (_('Facturación electrónica'), {
            'fields': ('AMBIENTE_FACTURACION', 'CLAVE_CERTIFICADO', 'RUTA_CERTIFICADO'),
            'classes': ('collapse',),
        }),
    )