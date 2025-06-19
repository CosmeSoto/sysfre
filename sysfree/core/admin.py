from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import ConfiguracionSistema, Empresa, Sucursal, LogActividad, Usuario, TipoIVA


@admin.register(ConfiguracionSistema)
class ConfiguracionSistemaAdmin(admin.ModelAdmin):
    list_display = ('NOMBRE_EMPRESA', 'RUC', 'get_iva_porcentaje', 'activo')
    list_filter = ('activo', 'AMBIENTE_FACTURACION')
    search_fields = ('NOMBRE_EMPRESA', 'RUC')
    autocomplete_fields = ['tipo_iva_default']
    
    def get_iva_porcentaje(self, obj):
        if obj.tipo_iva_default:
            return f"{obj.tipo_iva_default.nombre} ({obj.tipo_iva_default.porcentaje}%)"
        return "-"
    get_iva_porcentaje.short_description = _('IVA')
    fieldsets = (
        (None, {
            'fields': ('NOMBRE_EMPRESA', 'RUC', 'DIRECCION', 'TELEFONO', 'EMAIL', 'SITIO_WEB')
        }),
        (_('Numeración de Documentos'), {
            'fields': (
                'PREFIJO_FACTURA', 'INICIO_FACTURA',
                'PREFIJO_PROFORMA', 'INICIO_PROFORMA',
                'PREFIJO_NOTA_VENTA', 'INICIO_NOTA_VENTA',
                'PREFIJO_TICKET', 'INICIO_TICKET'
            )
        }),
        (_('Impuestos'), {
            'fields': ('tipo_iva_default',)
        }),
        (_('Facturación Electrónica'), {
            'fields': ('AMBIENTE_FACTURACION', 'CLAVE_CERTIFICADO', 'RUTA_CERTIFICADO')
        }),
        (_('Auditoría'), {
            'fields': ('activo', 'creado_por', 'modificado_por', 'fecha_creacion', 'fecha_modificacion')
        }),
    )
    readonly_fields = ('creado_por', 'modificado_por', 'fecha_creacion', 'fecha_modificacion')


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'ruc', 'telefono', 'email', 'activo')
    list_filter = ('activo', 'ambiente_facturacion')
    search_fields = ('nombre', 'ruc', 'email')
    fieldsets = (
        (None, {
            'fields': ('nombre', 'nombre_comercial', 'ruc', 'direccion', 'telefono', 'email', 'sitio_web', 'logo')
        }),
        (_('Información Fiscal'), {
            'fields': ('regimen_fiscal', 'representante_legal', 'cedula_representante')
        }),
        (_('Información Adicional'), {
            'fields': ('descripcion', 'horario')
        }),
        (_('Redes Sociales'), {
            'fields': ('facebook', 'instagram', 'twitter')
        }),
        (_('Facturación Electrónica'), {
            'fields': ('ambiente_facturacion', 'certificado_digital', 'clave_certificado')
        }),
        (_('Auditoría'), {
            'fields': ('activo', 'creado_por', 'modificado_por', 'fecha_creacion', 'fecha_modificacion')
        }),
    )
    readonly_fields = ('creado_por', 'modificado_por', 'fecha_creacion', 'fecha_modificacion')


@admin.register(Sucursal)
class SucursalAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'empresa', 'es_matriz', 'activo')
    list_filter = ('activo', 'es_matriz', 'empresa')
    search_fields = ('nombre', 'codigo', 'empresa__nombre')
    autocomplete_fields = ['empresa']
    fieldsets = (
        (None, {
            'fields': ('empresa', 'nombre', 'codigo', 'direccion', 'telefono', 'email', 'es_matriz', 'horario')
        }),
        (_('Auditoría'), {
            'fields': ('activo', 'creado_por', 'modificado_por', 'fecha_creacion', 'fecha_modificacion')
        }),
    )
    readonly_fields = ('creado_por', 'modificado_por', 'fecha_creacion', 'fecha_modificacion')


@admin.register(LogActividad)
class LogActividadAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'usuario', 'nivel', 'tipo', 'accion', 'modelo')
    list_filter = ('nivel', 'tipo', 'usuario')
    search_fields = ('accion', 'descripcion', 'modelo', 'objeto_id')
    fieldsets = (
        (None, {
            'fields': ('usuario', 'fecha', 'ip', 'nivel', 'tipo', 'accion', 'descripcion', 'modelo', 'objeto_id', 'datos')
        }),
    )
    readonly_fields = ('fecha', 'ip', 'usuario', 'nivel', 'tipo', 'accion', 'descripcion', 'modelo', 'objeto_id', 'datos')
    date_hierarchy = 'fecha'

    def has_add_permission(self, request):
        return False  # No permitir agregar logs manualmente

    def has_change_permission(self, request, obj=None):
        return False  # No permitir editar logs

    def has_delete_permission(self, request, obj=None):
        return False  # No permitir eliminar logs


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('email', 'nombres', 'apellidos', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff')
    search_fields = ('email', 'nombres', 'apellidos')
    fieldsets = (
        (None, {
            'fields': ('email', 'password', 'nombres', 'apellidos', 'telefono', 'foto', 'fecha_nacimiento')
        }),
        (_('Permisos'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Auditoría'), {
            'fields': ('fecha_creacion', 'fecha_modificacion', 'ultimo_login')
        }),
    )
    readonly_fields = ('fecha_creacion', 'fecha_modificacion', 'ultimo_login')
    filter_horizontal = ('groups', 'user_permissions')


@admin.register(TipoIVA)
class TipoIVAAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'porcentaje', 'es_default', 'activo')
    list_filter = ('activo', 'es_default')
    search_fields = ('nombre', 'codigo', 'descripcion')
    fieldsets = (
        (None, {
            'fields': ('nombre', 'codigo', 'porcentaje', 'descripcion', 'es_default')
        }),
        (_('Auditoría'), {
            'fields': ('activo', 'creado_por', 'modificado_por', 'fecha_creacion', 'fecha_modificacion')
        }),
    )
    readonly_fields = ('creado_por', 'modificado_por', 'fecha_creacion', 'fecha_modificacion')