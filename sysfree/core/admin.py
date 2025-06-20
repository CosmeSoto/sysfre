from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import ConfiguracionSistema, Empresa, Sucursal, LogActividad, Usuario, TipoIVA


@admin.register(ConfiguracionSistema)
class ConfiguracionSistemaAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'get_iva_porcentaje', 'activo')
    list_filter = ('activo',)
    
    def get_iva_porcentaje(self, obj):
        if obj.tipo_iva_default:
            return f"{obj.tipo_iva_default.nombre} ({obj.tipo_iva_default.porcentaje}%)"
        return "-"
    get_iva_porcentaje.short_description = _('IVA')
    fieldsets = (
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
            'classes': ('collapse',),
            'fields': (
                'ambiente_facturacion',
                'ruta_certificado',
                'clave_certificado',
                'url_recepcion_pruebas',
                'url_autorizacion_pruebas',
                'url_recepcion_produccion',
                'url_autorizacion_produccion',
            )
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
    list_display = ('fecha', 'usuario', 'nivel', 'tipo', 'accion', 'modelo', 'get_ip_short')
    list_filter = ('nivel', 'tipo', 'fecha', 'usuario')
    search_fields = ('accion', 'descripcion', 'modelo', 'objeto_id', 'ip')
    date_hierarchy = 'fecha'
    ordering = ('-fecha',)
    list_per_page = 50
    
    fieldsets = (
        (_('Información Principal'), {
            'fields': ('usuario', 'fecha', 'accion', 'descripcion')
        }),
        (_('Contexto'), {
            'fields': ('nivel', 'tipo', 'modelo', 'objeto_id', 'ip', 'user_agent')
        }),
        (_('Datos'), {
            'classes': ('collapse',),
            'fields': ('datos', 'datos_anteriores')
        }),
    )
    readonly_fields = ('fecha', 'ip', 'user_agent', 'usuario', 'nivel', 'tipo', 'accion', 
                      'descripcion', 'modelo', 'objeto_id', 'datos', 'datos_anteriores')
    
    def get_ip_short(self, obj):
        return obj.ip[:15] + '...' if obj.ip and len(obj.ip) > 15 else obj.ip or '-'
    get_ip_short.short_description = 'IP'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser  # Solo superusuarios pueden eliminar logs


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    list_display = ('email', 'nombres', 'apellidos', 'is_active', 'is_staff', 'is_superuser')
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    search_fields = ('email', 'nombres', 'apellidos')
    ordering = ('email',)
    
    fieldsets = (
        (None, {
            'fields': ('email', 'nombres', 'apellidos', 'telefono', 'foto', 'fecha_nacimiento')
        }),
        (_('Permisos'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Auditoría'), {
            'fields': ('fecha_creacion', 'fecha_modificacion', 'ultimo_login')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nombres', 'apellidos', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )
    
    readonly_fields = ('fecha_creacion', 'fecha_modificacion', 'ultimo_login')


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