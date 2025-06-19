from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.urls import reverse
from django.utils.html import format_html
from .models import Cliente, ContactoCliente, DireccionCliente
from ecommerce.models import Pedido
from .services.cliente_service import ClienteService
from core.models import Usuario
from django.utils.crypto import get_random_string

class ContactoClienteInline(admin.TabularInline):
    model = ContactoCliente
    extra = 0
    fields = ('nombres', 'apellidos', 'cargo', 'email', 'es_principal')
    readonly_fields = ('creado_por', 'fecha_creacion')
    can_delete = True
    max_num = 5

class DireccionClienteInline(admin.TabularInline):
    model = DireccionCliente
    extra = 0
    fields = ('tipo', 'nombre', 'direccion', 'ciudad', 'es_principal')
    readonly_fields = ('creado_por', 'fecha_creacion')
    can_delete = True
    max_num = 5

class PedidoInline(admin.TabularInline):
    model = Pedido
    extra = 0
    fields = ('numero', 'fecha', 'total', 'estado')
    readonly_fields = ('numero', 'fecha', 'total')
    can_delete = False
    verbose_name = _('pedido')
    verbose_name_plural = _('pedidos')
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('cliente')

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = (
        'identificacion',
        'nombre_completo',
        'tipo_cliente',
        'email',
        'telefono',
        'num_direcciones',
        'num_contactos',
        'num_pedidos',
        'recibir_promociones',
        'tiene_acceso_portal',
        'activo',
    )
    list_filter = (
        'tipo_cliente',
        'tipo_identificacion',
        'activo',
        'recibir_promociones',
        # 'usuario__is_active',
        'direcciones__provincia',
    )
    search_fields = ('identificacion', 'nombres', 'apellidos', 'nombre_comercial', 'email')
    readonly_fields = ('fecha_creacion', 'fecha_modificacion', 'creado_por', 'modificado_por')
    inlines = [ContactoClienteInline, DireccionClienteInline, PedidoInline]
    actions = ['activar_clientes', 'desactivar_clientes', 'enviar_correo_bienvenida']
    ordering = ('apellidos', 'nombres')
    autocomplete_fields = ['usuario']

    fieldsets = (
        (None, {'fields': ('tipo_identificacion', 'identificacion')}),
        (_('Información personal'), {
            'fields': ('tipo_cliente', 'nombres', 'apellidos', 'nombre_comercial', 'fecha_nacimiento')
        }),
        (_('Contacto'), {'fields': ('email', 'telefono', 'celular', 'direccion')}),
        (_('Crédito'), {'fields': ('limite_credito', 'dias_credito')}),
        (_('Portal de cliente'), {'fields': ('usuario', 'recibir_promociones')}),
        (_('Auditoría'), {
            'fields': ('activo', 'creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('usuario').prefetch_related('direcciones', 'contactos', 'pedidos')

    def num_direcciones(self, obj):
        return obj.direcciones.count()
    num_direcciones.short_description = _('Nº Direcciones')

    def num_contactos(self, obj):
        return obj.contactos.count()
    num_contactos.short_description = _('Nº Contactos')

    def num_pedidos(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:ecommerce_pedido_changelist') + f'?cliente__id__exact={obj.id}',
            obj.pedidos.count()
        )
    num_pedidos.short_description = _('Nº Pedidos')

    def activar_clientes(self, request, queryset):
        updated = queryset.update(activo=True)
        self.message_user(request, f"{updated} clientes activados correctamente.", messages.SUCCESS)
    activar_clientes.short_description = _('Activar clientes seleccionados')

    def desactivar_clientes(self, request, queryset):
        updated = queryset.update(activo=False)
        self.message_user(request, f"{updated} clientes desactivados correctamente.", messages.SUCCESS)
    desactivar_clientes.short_description = _('Desactivar clientes seleccionados')

    def enviar_correo_bienvenida(self, request, queryset):
        for cliente in queryset.filter(usuario__isnull=False, email__isnull=False):
            if cliente.email and cliente.tiene_acceso_portal:
                try:
                    password = get_random_string(12)
                    cliente.usuario.set_password(password)
                    cliente.usuario.save()
                    ClienteService.send_welcome_email(cliente, password)
                    self.message_user(
                        request,
                        f"Correo de bienvenida enviado a {cliente.nombre_completo}",
                        messages.SUCCESS
                    )
                except Exception as e:
                    self.message_user(
                        request,
                        f"Error al enviar correo a {cliente.nombre_completo}: {str(e)}",
                        messages.ERROR
                    )
            else:
                self.message_user(
                    request,
                    f"No se pudo enviar correo a {cliente.nombre_completo}: falta email o usuario inactivo",
                    messages.WARNING
                )
    enviar_correo_bienvenida.short_description = _('Enviar correo de bienvenida')

    def save_model(self, request, obj, form, change):
        if obj.limite_credito < 0:
            self.message_user(request, _("El límite de crédito no puede ser negativo."), messages.ERROR)
            return
        if obj.dias_credito < 0:
            self.message_user(request, _("Los días de crédito no pueden ser negativos."), messages.ERROR)
            return
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        readonly = super().get_readonly_fields(request, obj)
        return readonly


@admin.register(ContactoCliente)
class ContactoClienteAdmin(admin.ModelAdmin):
    list_display = ('nombres', 'apellidos', 'cliente', 'cargo', 'email', 'telefono', 'es_principal', 'activo')
    list_filter = ('es_principal', 'activo', 'cliente__tipo_cliente')
    search_fields = (
        'nombres', 'apellidos', 'email',
        'cliente__nombres', 'cliente__apellidos', 'cliente__nombre_comercial'
    )
    readonly_fields = ('fecha_creacion', 'fecha_modificacion', 'creado_por', 'modificado_por')
    autocomplete_fields = ['cliente']

    fieldsets = (
        (None, {'fields': ('cliente', 'nombres', 'apellidos', 'cargo')}),
        (_('Contacto'), {'fields': ('email', 'telefono', 'celular')}),
        (_('Información adicional'), {'fields': ('es_principal', 'notas')}),
        (_('Auditoría'), {
            'fields': ('activo', 'creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('cliente__usuario')


@admin.register(DireccionCliente)
class DireccionClienteAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'tipo', 'nombre', 'ciudad', 'provincia', 'es_principal', 'activo')
    list_filter = ('tipo', 'es_principal', 'activo', 'provincia')
    search_fields = (
        'nombre', 'direccion', 'ciudad', 'provincia',
        'cliente__nombres', 'cliente__apellidos', 'cliente__nombre_comercial'
    )
    readonly_fields = ('fecha_creacion', 'fecha_modificacion', 'creado_por', 'modificado_por')
    autocomplete_fields = ['cliente']

    fieldsets = (
        (None, {'fields': ('cliente', 'tipo', 'nombre')}),
        (_('Dirección'), {'fields': ('direccion', 'ciudad', 'provincia', 'codigo_postal')}),
        (_('Geolocalización'), {'fields': ('latitud', 'longitud')}),
        (_('Información adicional'), {'fields': ('es_principal', 'notas')}),
        (_('Auditoría'), {
            'fields': ('activo', 'creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('cliente__usuario')