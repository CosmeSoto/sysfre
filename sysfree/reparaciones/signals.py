from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Reparacion, SeguimientoReparacion, RepuestoReparacion
from inventario.services.inventario_service import InventarioService

# Las señales de auditoría están en core.signals


@receiver(pre_save, sender=Reparacion)
def registrar_seguimiento_reparacion(sender, instance, **kwargs):
    """
    Registra un seguimiento cuando cambia el estado de una reparación.
    """
    if instance.pk:  # Solo si ya existe (no es nueva)
        try:
            # Obtener el estado anterior
            reparacion_anterior = Reparacion.objects.get(pk=instance.pk)
            
            # Si cambió el estado, registrar seguimiento
            if reparacion_anterior.estado != instance.estado:
                # Guardar el estado anterior para usarlo después del save
                instance._estado_anterior = reparacion_anterior.estado
                
                # Si el estado nuevo es 'entregado', registrar la fecha de entrega
                if instance.estado == 'entregado' and not instance.fecha_entrega:
                    instance.fecha_entrega = timezone.now()
        except Reparacion.DoesNotExist:
            pass


@receiver(post_save, sender=Reparacion)
def crear_seguimiento_reparacion(sender, instance, created, **kwargs):
    """
    Crea un seguimiento después de guardar una reparación.
    """
    # Si es nueva, crear el primer seguimiento
    if created:
        SeguimientoReparacion.objects.create(
            reparacion=instance,
            estado_nuevo=instance.estado,
            comentario='Reparación registrada',
            creado_por=instance.creado_por,
            modificado_por=instance.modificado_por
        )
    # Si cambió el estado, crear seguimiento
    elif hasattr(instance, '_estado_anterior') and instance._estado_anterior != instance.estado:
        SeguimientoReparacion.objects.create(
            reparacion=instance,
            estado_anterior=instance._estado_anterior,
            estado_nuevo=instance.estado,
            comentario=f'Estado cambiado de {instance._estado_anterior} a {instance.estado}',
            creado_por=instance.modificado_por,
            modificado_por=instance.modificado_por
        )


@receiver(post_save, sender=RepuestoReparacion)
def actualizar_costo_repuestos(sender, instance, created, **kwargs):
    """
    Actualiza el costo de repuestos de la reparación cuando se agrega o modifica un repuesto.
    """
    reparacion = instance.reparacion
    repuestos = reparacion.repuestos.all()
    
    # Calcular el costo total de repuestos
    costo_repuestos = sum(repuesto.subtotal for repuesto in repuestos)
    
    # Actualizar la reparación
    reparacion.costo_repuestos = costo_repuestos
    reparacion.save(update_fields=['costo_repuestos', 'total'])
    
    # Registrar movimiento de inventario si es un repuesto nuevo
    if created and instance.producto.es_inventariable:
        try:
            InventarioService.registrar_salida(
                producto=instance.producto,
                cantidad=instance.cantidad,
                origen='reparacion',
                documento=reparacion.numero,
                notas=f'Repuesto para reparación #{reparacion.numero}',
                usuario=instance.creado_por,
                referencia_id=reparacion.id,
                referencia_tipo='reparacion'
            )
        except ValueError:
            # Manejar el caso de stock insuficiente
            pass