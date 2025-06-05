from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import Venta, DetalleVenta, Pago
from inventario.services.inventario_service import InventarioService


@receiver(post_save, sender=DetalleVenta)
def actualizar_totales_venta(sender, instance, created, **kwargs):
    """
    Actualiza los totales de la venta cuando se crea o modifica un detalle.
    """
    venta = instance.venta
    detalles = venta.detalles.all()
    
    # Calcular totales
    subtotal = sum(detalle.subtotal for detalle in detalles)
    iva = sum(detalle.iva for detalle in detalles)
    descuento = sum(detalle.descuento for detalle in detalles)
    total = subtotal + iva - descuento
    
    # Actualizar venta
    venta.subtotal = subtotal
    venta.iva = iva
    venta.descuento = descuento
    venta.total = total
    venta.save(update_fields=['subtotal', 'iva', 'descuento', 'total'])


@receiver(post_delete, sender=DetalleVenta)
def actualizar_totales_venta_eliminacion(sender, instance, **kwargs):
    """
    Actualiza los totales de la venta cuando se elimina un detalle.
    """
    venta = instance.venta
    detalles = venta.detalles.all()
    
    # Calcular totales
    subtotal = sum(detalle.subtotal for detalle in detalles)
    iva = sum(detalle.iva for detalle in detalles)
    descuento = sum(detalle.descuento for detalle in detalles)
    total = subtotal + iva - descuento
    
    # Actualizar venta
    venta.subtotal = subtotal
    venta.iva = iva
    venta.descuento = descuento
    venta.total = total
    venta.save(update_fields=['subtotal', 'iva', 'descuento', 'total'])


@receiver(post_save, sender=Pago)
def actualizar_estado_venta_pago(sender, instance, created, **kwargs):
    """
    Actualiza el estado de la venta cuando se registra un pago.
    """
    if instance.estado == 'aprobado':
        venta = instance.venta
        pagos_aprobados = venta.pagos.filter(estado='aprobado')
        total_pagado = sum(pago.monto for pago in pagos_aprobados)
        
        # Si el total pagado es igual o mayor al total de la venta, marcar como pagado
        if total_pagado >= venta.total and venta.estado == 'pendiente':
            venta.estado = 'pagado'
            venta.fecha_pago = timezone.now()
            venta.save(update_fields=['estado', 'fecha_pago'])


@receiver(post_save, sender=Venta)
def registrar_movimiento_inventario(sender, instance, created, **kwargs):
    """
    Registra movimientos de inventario cuando una venta cambia de estado.
    """
    # Solo procesar si la venta está pagada y no se han registrado movimientos
    if instance.estado == 'pagado' and not hasattr(instance, '_movimientos_registrados'):
        for detalle in instance.detalles.all():
            if detalle.producto.es_inventariable:
                try:
                    InventarioService.registrar_salida(
                        producto=detalle.producto,
                        cantidad=detalle.cantidad,
                        origen='venta',
                        documento=instance.numero,
                        notas=f'Venta #{instance.numero}',
                        usuario=instance.modificado_por,
                        referencia_id=instance.id,
                        referencia_tipo='venta'
                    )
                except ValueError:
                    # Manejar el caso de stock insuficiente
                    pass
        
        # Marcar que ya se registraron los movimientos
        instance._movimientos_registrados = True