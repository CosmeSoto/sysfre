from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Cliente, ContactoCliente, DireccionCliente


class ContactoClienteInline(admin.TabularInline):
    model = ContactoCliente
    extra = 0
    fields = ('nombres', 'apellidos', 'cargo', 'email', 'telefono', 'es_principal')


class DireccionClienteInline(admin.TabularInline):
    model = DireccionCliente
    extra = 0
    fields = ('tipo', 'nombre', 'direccion', 'ciudad', 'provincia', 'es_principal')


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('identificacion', 'nombre_completo', 'tipo_cliente', 'email', 'telefono', 'activo')
    list_filter = ('tipo_cliente', 'tipo_identificacion', 'activo')
    search_fields = ('identificacion', 'nombres', 'apellidos', 'nombre_comercial', 'email')
    readonly_fields = ('fecha_creacion', 'fecha_modificacion', 'creado_por', 'modificado_por')
    inlines = [ContactoClienteInline, DireccionClienteInline]
    
    fieldsets = (
        (None, {'fields': ('tipo_identificacion', 'identificacion')}),
        (_('Información personal'), {'fields': ('tipo_cliente', 'nombres', 'apellidos', 'nombre_comercial', 'fecha_nacimiento')}),
        (_('Contacto'), {'fields': ('email', 'telefono', 'celular', 'direccion')}),
        (_('Crédito'), {'fields': ('limite_credito', 'dias_credito')}),
        (_('Portal de cliente'), {'fields': ('usuario', 'recibir_promociones')}),
        (_('Auditoría'), {'fields': ('activo', 'creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')}),
    )


@admin.register(ContactoCliente)
class ContactoClienteAdmin(admin.ModelAdmin):
    list_display = ('nombres', 'apellidos', 'cliente', 'cargo', 'email', 'telefono', 'es_principal')
    list_filter = ('es_principal', 'activo')
    search_fields = ('nombres', 'apellidos', 'email', 'cliente__nombres', 'cliente__apellidos', 'cliente__nombre_comercial')
    readonly_fields = ('fecha_creacion', 'fecha_modificacion', 'creado_por', 'modificado_por')
    
    fieldsets = (
        (None, {'fields': ('cliente', 'nombres', 'apellidos', 'cargo')}),
        (_('Contacto'), {'fields': ('email', 'telefono', 'celular')}),
        (_('Información adicional'), {'fields': ('es_principal', 'notas')}),
        (_('Auditoría'), {'fields': ('activo', 'creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')}),
    )


@admin.register(DireccionCliente)
class DireccionClienteAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'tipo', 'nombre', 'ciudad', 'provincia', 'es_principal')
    list_filter = ('tipo', 'es_principal', 'activo')
    search_fields = ('nombre', 'direccion', 'ciudad', 'provincia', 'cliente__nombres', 'cliente__apellidos', 'cliente__nombre_comercial')
    readonly_fields = ('fecha_creacion', 'fecha_modificacion', 'creado_por', 'modificado_por')
    
    fieldsets = (
        (None, {'fields': ('cliente', 'tipo', 'nombre')}),
        (_('Dirección'), {'fields': ('direccion', 'ciudad', 'provincia', 'codigo_postal')}),
        (_('Geolocalización'), {'fields': ('latitud', 'longitud')}),
        (_('Información adicional'), {'fields': ('es_principal', 'notas')}),
        (_('Auditoría'), {'fields': ('activo', 'creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')}),
    )