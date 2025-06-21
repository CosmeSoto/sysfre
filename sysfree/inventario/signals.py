from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models.orden_compra import OrdenCompra
from .models.movimiento import MovimientoInventario
from .models.stock_almacen import StockAlmacen
from .models.almacen import Almacen
from .services.inventario_service import InventarioService
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

# Las señales de auditoría están en core.signals

@receiver(post_save, sender=MovimientoInventario)
def actualizar_stock_producto(sender, instance, created, **kwargs):
    """
    Actualiza las fechas de último movimiento y última compra si corresponde.
    """
    logger.debug(f"Procesando señal post_save para MovimientoInventario {instance.id}, creado: {created}")
    if created:
        producto = instance.producto
        
        # Actualizar fecha de último movimiento
        producto.fecha_ultimo_movimiento = timezone.now()
        
        # Si es una entrada por compra, actualizar fecha de última compra
        if instance.tipo == 'entrada' and instance.origen == 'compra':
            producto.fecha_ultima_compra = timezone.now().date()
        
        producto.save(update_fields=['fecha_ultimo_movimiento', 'fecha_ultima_compra'])
        logger.debug(f"Producto {producto.id} actualizado: fecha_ultimo_movimiento={producto.fecha_ultimo_movimiento}")

@receiver(pre_save, sender=MovimientoInventario)
def calcular_stock_nuevo(sender, instance, **kwargs):
    """
    Calcula el stock nuevo basado en el stock anterior y la cantidad del movimiento.
    """
    logger.debug(f"Procesando señal pre_save para MovimientoInventario {instance}")
    if not instance.pk:  # Solo para nuevos movimientos
        producto = instance.producto
        stock_almacen = StockAlmacen.objects.filter(producto=producto, almacen=instance.almacen).first()
        instance.stock_anterior = stock_almacen.cantidad if stock_almacen else Decimal('0.00')
        
        if instance.tipo == 'entrada':
            instance.stock_nuevo = instance.stock_anterior + instance.cantidad
        elif instance.tipo == 'salida':
            instance.stock_nuevo = instance.stock_anterior - instance.cantidad
        elif instance.tipo == 'ajuste':
            instance.stock_nuevo = instance.cantidad
        else:
            instance.stock_nuevo = instance.stock_anterior
        logger.debug(f"Stock nuevo calculado: {instance.stock_nuevo} para producto {producto.id}")

@receiver(post_save, sender=OrdenCompra)
def crear_movimiento_compra(sender, instance, created, **kwargs):
    """
    Crea un MovimientoInventario cuando una OrdenCompra se completa.
    """
    logger.info(f"Procesando OrdenCompra {instance.id}, estado: {instance.estado}, creado: {created}")
    if instance.estado == 'completada':
        almacen = Almacen.objects.filter(activo=True).first()
        if not almacen:
            logger.error("No se encontró almacén activo para crear movimiento de compra")
            raise ValueError("No hay almacenes activos disponibles para registrar el movimiento.")
        
        for item in instance.items.all():
            # Evitar crear movimientos duplicados
            if not MovimientoInventario.objects.filter(
                referencia_id=instance.id,
                referencia_tipo='orden_compra',
                producto=item.producto
            ).exists():
                logger.info(f"Creando movimiento para producto {item.producto.id} en almacén {almacen.id}")
                try:
                    movimiento = InventarioService.registrar_entrada(
                        producto=item.producto,
                        cantidad=item.cantidad,
                        origen='compra',
                        costo_unitario=item.precio_unitario,
                        proveedor=instance.proveedor,
                        almacen=almacen,
                        referencia_id=instance.id,
                        referencia_tipo='orden_compra'
                    )
                    logger.info(f"Movimiento creado: {movimiento.id}")
                except Exception as e:
                    logger.error(f"Error al crear movimiento para producto {item.producto.id}: {str(e)}")
                    raise