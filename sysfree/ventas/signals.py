from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import Venta, DetalleVenta, Pago, NotaCredito, DetalleNotaCredito
from inventario.services.inventario_service import InventarioService

# Las señales de auditoría están en core.signals


@receiver(post_save, sender=DetalleVenta)
def actualizar_totales_venta(sender, instance, created, **kwargs):
    """Actualiza los totales de la venta cuando se crea o modifica un detalle."""
    venta = instance.venta
    detalles = venta.detalles.all()
    
    subtotal = sum(detalle.subtotal for detalle in detalles)
    iva = sum(detalle.iva for detalle in detalles)
    descuento = sum(detalle.descuento for detalle in detalles)
    total = subtotal + iva - descuento
    
    venta.subtotal = subtotal
    venta.iva = iva
    venta.descuento = descuento
    venta.total = total
    venta.save(update_fields=['subtotal', 'iva', 'descuento', 'total'])


@receiver(post_delete, sender=DetalleVenta)
def actualizar_totales_venta_eliminacion(sender, instance, **kwargs):
    """Actualiza los totales de la venta cuando se elimina un detalle."""
    venta = instance.venta
    detalles = venta.detalles.all()
    
    subtotal = sum(detalle.subtotal for detalle in detalles)
    iva = sum(detalle.iva for detalle in detalles)
    descuento = sum(detalle.descuento for detalle in detalles)
    total = subtotal + iva - descuento
    
    venta.subtotal = subtotal
    venta.iva = iva
    venta.descuento = descuento
    venta.total = total
    venta.save(update_fields=['subtotal', 'iva', 'descuento', 'total'])


@receiver(post_save, sender=Pago)
def actualizar_estado_venta_pago(sender, instance, created, **kwargs):
    """Actualiza el estado de la venta cuando se registra un pago."""
    if instance.estado == 'aprobado':
        venta = instance.venta
        pagos_aprobados = venta.pagos.filter(estado='aprobado')
        total_pagado = sum(pago.monto for pago in pagos_aprobados)
        
        if total_pagado >= venta.total and venta.estado not in ['pagada', 'anulada']:
            venta.estado = 'pagada'
            venta.fecha_pago = timezone.now()
            venta.save(update_fields=['estado', 'fecha_pago'])


@receiver(post_save, sender=Venta)
def registrar_movimiento_inventario_venta(sender, instance, created, **kwargs):
    """Registra movimientos de inventario para ventas pagadas."""
    if instance.estado == 'pagada' and not hasattr(instance, '_movimientos_registrados'):
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
                except ValueError as e:
                    # Manejar el caso de stock insuficiente
                    pass
        instance._movimientos_registrados = True


@receiver(post_save, sender=DetalleNotaCredito)
def actualizar_totales_nota_credito(sender, instance, created, **kwargs):
    """Actualiza los totales de la nota de crédito cuando se crea o modifica un detalle."""
    nota = instance.nota_credito
    detalles = nota.detalles.all()
    
    subtotal = sum(detalle.subtotal for detalle in detalles)
    iva = sum(detalle.iva for detalle in detalles)
    total = subtotal + iva
    
    nota.subtotal = subtotal
    nota.iva = iva
    nota.total = total
    nota.save(update_fields=['subtotal', 'iva', 'total'])


@receiver(post_delete, sender=DetalleNotaCredito)
def actualizar_totales_nota_credito_eliminacion(sender, instance, **kwargs):
    """Actualiza los totales de la nota de crédito cuando se elimina un detalle."""
    nota = instance.nota_credito
    detalles = nota.detalles.all()
    
    subtotal = sum(detalle.subtotal for detalle in detalles)
    iva = sum(detalle.iva for detalle in detalles)
    total = subtotal + iva
    
    nota.subtotal = subtotal
    nota.iva = iva
    nota.total = total
    nota.save(update_fields=['subtotal', 'iva', 'total'])


@receiver(post_save, sender=NotaCredito)
def registrar_movimiento_inventario_nota_credito(sender, instance, created, **kwargs):
    """Registra movimientos de inventario para notas de crédito emitidas."""
    if instance.estado == 'emitida' and not hasattr(instance, '_movimientos_registrados'):
        for detalle in instance.detalles.all():
            if detalle.producto.es_inventariable:
                try:
                    InventarioService.registrar_entrada(
                        producto=detalle.producto,
                        cantidad=detalle.cantidad,
                        origen='nota_credito',
                        documento=instance.numero,
                        notas=f'Nota de crédito #{instance.numero}',
                        usuario=instance.modificado_por,
                        referencia_id=instance.id,
                        referencia_tipo='nota_credito'
                    )
                except ValueError as e:
                    # Manejar errores
                    pass
        instance._movimientos_registrados = True