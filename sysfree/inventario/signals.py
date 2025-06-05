from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Producto, MovimientoInventario


@receiver(post_save, sender=MovimientoInventario)
def actualizar_stock_producto(sender, instance, created, **kwargs):
    """
    Actualiza el stock del producto cuando se crea un movimiento de inventario.
    También actualiza las fechas de último movimiento y última compra si corresponde.
    """
    if created:
        producto = instance.producto
        
        # Actualizar fecha de último movimiento
        producto.fecha_ultimo_movimiento = timezone.now()
        
        # Si es una entrada por compra, actualizar fecha de última compra
        if instance.tipo == 'entrada' and instance.origen == 'compra':
            producto.fecha_ultima_compra = timezone.now().date()
        
        producto.save(update_fields=['fecha_ultimo_movimiento', 'fecha_ultima_compra'])


@receiver(pre_save, sender=MovimientoInventario)
def calcular_stock_nuevo(sender, instance, **kwargs):
    """
    Calcula el stock nuevo basado en el stock anterior y la cantidad del movimiento.
    """
    if not instance.pk:  # Solo para nuevos movimientos
        producto = instance.producto
        instance.stock_anterior = producto.stock
        
        if instance.tipo == 'entrada':
            instance.stock_nuevo = producto.stock + instance.cantidad
        elif instance.tipo == 'salida':
            instance.stock_nuevo = producto.stock - instance.cantidad
        elif instance.tipo == 'ajuste':
            # En ajustes, la cantidad es el nuevo valor absoluto
            instance.stock_nuevo = instance.cantidad
        else:
            instance.stock_nuevo = producto.stock
        
        # Actualizar el stock del producto
        producto.stock = instance.stock_nuevo
        producto.save(update_fields=['stock'])