from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import ModeloBase, TipoIVA, Empresa, Sucursal, ConfiguracionSistema, Usuario
from clientes.models import Cliente, ContactoCliente, DireccionCliente
from inventario.models import (Producto, Categoria, Proveedor, MovimientoInventario, AlertaStock, 
                             Almacen, OrdenCompra, ItemOrdenCompra, StockAlmacen, Lote)
from .middleware import get_usuario_actual, get_request_actual
from .services.log_service import LogService
from .services import IVAService
from .constants import TiposActividad, MensajesAuditoria

# Modelos que serán auditados automáticamente
AUDITED_MODELS = [
    # Core
    TipoIVA, Empresa, Sucursal, ConfiguracionSistema, Usuario,
    # Clientes
    Cliente, ContactoCliente, DireccionCliente,
    # Inventario
    Producto, Categoria, Proveedor, MovimientoInventario, AlertaStock,
    Almacen, OrdenCompra, ItemOrdenCompra, StockAlmacen, Lote
]


def get_client_info(request):
    """Extrae IP y User-Agent del request."""
    if not request:
        return None, None
    
    ip = request.META.get('REMOTE_ADDR')
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    return ip, user_agent


def serialize_instance(instance, fields=None):
    """Serializa una instancia de modelo a un diccionario excluyendo campos sensibles."""
    # Campos excluidos por seguridad y auditoría
    excluded_fields = {
        'creado_por', 'modificado_por', 'fecha_creacion', 'fecha_modificacion', 'activo',
        'password', 'last_login', 'user_permissions', 'groups',  # Campos sensibles de Usuario
        'clave_certificado', 'url_recepcion_pruebas', 'url_autorizacion_pruebas',  # Datos fiscales sensibles
    }
    
    opts = instance._meta
    data = {}
    for f in opts.concrete_fields:
        if f.name in excluded_fields:
            continue
        if fields and f.name not in fields:
            continue
        
        value = getattr(instance, f.name)
        
        # Manejar diferentes tipos de campos
        if f.many_to_one and value is not None:
            value = value.pk
        elif hasattr(f, 'upload_to'):  # FileField/ImageField
            value = str(value) if value else None
        elif hasattr(value, 'isoformat'):  # DateField/DateTimeField
            value = value.isoformat()
        elif not isinstance(value, (str, int, float, bool, type(None))):
            value = str(value)
            
        data[f.name] = value
    
    # Para Usuario, solo incluir campos seguros
    if instance._meta.model_name == 'usuario':
        safe_fields = {'email', 'nombres', 'apellidos', 'telefono', 'is_active', 'is_staff', 'fecha_nacimiento'}
        data = {k: v for k, v in data.items() if k in safe_fields}
    
    return data


@receiver(pre_save)
def pre_save_modelo_base(sender, instance, **kwargs):
    """
    Signal para asignar automáticamente el usuario actual a los campos
    creado_por y modificado_por en modelos que heredan de ModeloBase.
    """
    if not issubclass(sender, ModeloBase):
        return
    
    usuario_actual = get_usuario_actual()
    
    # Si es un objeto nuevo (no tiene ID), asignar el usuario actual como creador
    if not instance.pk and usuario_actual and usuario_actual.is_authenticated:
        instance.creado_por = usuario_actual
    
    # Siempre asignar el usuario actual como modificador
    if usuario_actual and usuario_actual.is_authenticated:
        instance.modificado_por = usuario_actual


@receiver(pre_save)
def auditar_cambios_pre_save(sender, instance, **kwargs):
    """Antes de guardar, captura el estado anterior del objeto."""
    if sender in AUDITED_MODELS and instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            instance._old_state = serialize_instance(old_instance)
        except sender.DoesNotExist:
            instance._old_state = None


@receiver(post_save)
def auditar_cambios_post_save(sender, instance, created, **kwargs):
    """Después de guardar, registra la creación o actualización."""
    if sender not in AUDITED_MODELS:
        return

    usuario_actual = get_usuario_actual()
    request_actual = get_request_actual()
    ip, user_agent = get_client_info(request_actual)
    
    modelo_nombre = sender._meta.verbose_name.title()
    datos_actuales = serialize_instance(instance)

    if created:
        accion = f"CREACION_{sender.__name__.upper()}"
        descripcion = MensajesAuditoria.creacion(modelo_nombre, str(instance), usuario_actual)
        LogService.registrar_actividad(
            accion=accion, descripcion=descripcion, usuario=usuario_actual,
            modelo=sender.__name__, objeto_id=instance.pk, datos=datos_actuales,
            ip=ip, user_agent=user_agent, tipo=TiposActividad.NEGOCIO
        )
    else:
        datos_anteriores = getattr(instance, '_old_state', None)
        if datos_anteriores != datos_actuales:
            accion = f"ACTUALIZACION_{sender.__name__.upper()}"
            descripcion = MensajesAuditoria.actualizacion(modelo_nombre, str(instance), usuario_actual)
            LogService.registrar_actividad(
                accion=accion, descripcion=descripcion, usuario=usuario_actual,
                modelo=sender.__name__, objeto_id=instance.pk, datos=datos_actuales,
                datos_anteriores=datos_anteriores, ip=ip, user_agent=user_agent, tipo=TiposActividad.NEGOCIO
            )


@receiver(post_delete)
def auditar_eliminaciones(sender, instance, **kwargs):
    """Después de eliminar, registra la eliminación."""
    if sender not in AUDITED_MODELS:
        return

    usuario_actual = get_usuario_actual()
    request_actual = get_request_actual()
    ip, user_agent = get_client_info(request_actual)
    modelo_nombre = sender._meta.verbose_name.title()
    datos_eliminados = serialize_instance(instance)

    accion = f"ELIMINACION_{sender.__name__.upper()}"
    descripcion = MensajesAuditoria.eliminacion(modelo_nombre, str(instance), usuario_actual)
    LogService.registrar_actividad(
        accion=accion, descripcion=descripcion, usuario=usuario_actual,
        modelo=sender.__name__, objeto_id=instance.pk, datos_anteriores=datos_eliminados,
        ip=ip, user_agent=user_agent, tipo=TiposActividad.NEGOCIO
    )


# Las señales de autenticación están en mixins/auditoria_mixins.py


@receiver(post_save, sender=TipoIVA)
def invalidar_cache_iva_al_guardar(sender, instance, **kwargs):
    """
    Signal para invalidar la caché de IVA cuando se modifica un TipoIVA.
    """
    IVAService.invalidar_cache()


@receiver(post_delete, sender=TipoIVA)
def invalidar_cache_iva_al_eliminar(sender, instance, **kwargs):
    """
    Signal para invalidar la caché de IVA cuando se elimina un TipoIVA.
    """
    IVAService.invalidar_cache()