from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Pedido, DetallePedido, PagoOnline, ProductoEcommerce
from ventas.services.venta_service import VentaService
from inventario.services.inventario_service import InventarioService

# Las señales de auditoría están en core.signals


@receiver(post_save, sender=Pedido)
def actualizar_totales_pedido(sender, instance, created, **kwargs):
    """
    Actualiza los totales del pedido cuando se crea o modifica.
    """
    if hasattr(instance, '_skip_signal'):
        return
    
    detalles = instance.detalles.all()
    
    # Calcular totales
    subtotal = sum(detalle.subtotal for detalle in detalles)
    impuestos = sum(detalle.impuestos for detalle in detalles)
    total = subtotal + impuestos + instance.envio - instance.descuento
    
    # Actualizar pedido
    instance._skip_signal = True
    instance.subtotal = subtotal
    instance.impuestos = impuestos
    instance.total = total
    instance.save(update_fields=['subtotal', 'impuestos', 'total'])
    delattr(instance, '_skip_signal')


@receiver(post_save, sender=PagoOnline)
def actualizar_estado_pedido(sender, instance, created, **kwargs):
    """
    Actualiza el estado del pedido cuando se registra un pago.
    """
    if instance.estado == 'completado':
        pedido = instance.pedido
        pagos_completados = pedido.pagos.filter(estado='completado')
        total_pagado = sum(pago.monto for pago in pagos_completados)
        
        # Si el total pagado es igual o mayor al total del pedido, marcar como pagado
        if total_pagado >= pedido.total and pedido.estado == 'pendiente':
            pedido.estado = 'pagado'
            pedido.fecha_pago = timezone.now()
            pedido.save(update_fields=['estado', 'fecha_pago'])
            
            # Crear factura si no existe
            if not pedido.factura:
                # Convertir pedido a factura
                crear_factura_desde_pedido(pedido)


@receiver(post_save, sender=Pedido)
def registrar_movimientos_inventario(sender, instance, **kwargs):
    """
    Registra movimientos de inventario cuando un pedido cambia a estado pagado.
    """
    # Solo procesar si el pedido está pagado y no se han registrado movimientos
    if instance.estado == 'pagado' and not hasattr(instance, '_movimientos_registrados'):
        for detalle in instance.detalles.all():
            # Verificar si es un producto (no un servicio) y es inventariable
            if not detalle.es_servicio and detalle.producto and detalle.producto.es_inventariable:
                try:
                    # Buscar un almacén activo para registrar la salida
                    from inventario.models import Almacen
                    almacen = Almacen.objects.filter(activo=True).first()
                    
                    if not almacen:
                        import logging
                        logger = logging.getLogger('sysfree')
                        logger.error(f"No se encontró un almacén activo para registrar la salida del pedido {instance.numero}")
                        continue
                    
                    InventarioService.registrar_salida(
                        producto=detalle.producto,
                        cantidad=detalle.cantidad,
                        origen='venta',
                        documento=instance.numero,
                        notas=f'Pedido online #{instance.numero}',
                        usuario=instance.modificado_por,
                        referencia_id=instance.id,
                        referencia_tipo='pedido',
                        almacen=almacen
                    )
                    
                    import logging
                    logger = logging.getLogger('sysfree')
                    logger.info(f"Salida de inventario registrada para producto {detalle.producto.codigo} - {detalle.producto.nombre}, cantidad {detalle.cantidad}, pedido {instance.numero}")
                    
                    # Verificar si el stock está bajo el umbral mínimo
                    if detalle.producto.stock <= detalle.producto.stock_minimo:
                        from inventario.services.stock_notification_service import StockNotificationService
                        StockNotificationService.notificar_stock_bajo(detalle.producto)
                    
                except ValueError as e:
                    # Manejar el caso de stock insuficiente
                    import logging
                    logger = logging.getLogger('sysfree')
                    logger.error(f"Error al registrar salida de inventario para pedido {instance.numero}: {str(e)}")
                    
                except Exception as e:
                    import logging
                    logger = logging.getLogger('sysfree')
                    logger.error(f"Error inesperado al registrar salida de inventario para pedido {instance.numero}: {str(e)}")
        
        # Marcar que ya se registraron los movimientos
        instance._movimientos_registrados = True


@receiver(post_save, sender=DetallePedido)
def actualizar_estadisticas_producto(sender, instance, created, **kwargs):
    """
    Actualiza las estadísticas de ventas del producto cuando se crea un detalle de pedido.
    """
    if created:
        try:
            producto_ecommerce = ProductoEcommerce.objects.get(producto=instance.producto)
            producto_ecommerce.ventas += instance.cantidad
            producto_ecommerce.save(update_fields=['ventas'])
        except ProductoEcommerce.DoesNotExist:
            pass


def crear_factura_desde_pedido(pedido):
    """
    Crea una factura a partir de un pedido.
    
    Args:
        pedido: Pedido a partir del cual se crea la factura
    """
    # Preparar los items para la venta
    items = []
    for detalle in pedido.detalles.all():
        items.append({
            'producto_id': detalle.producto.id,
            'cantidad': detalle.cantidad,
            'precio_unitario': detalle.precio_unitario,
            'descuento': 0
        })
    
    # Crear la venta
    venta = VentaService.crear_venta(
        cliente=pedido.cliente,
        tipo='factura',
        items=items,
        direccion_facturacion=pedido.direccion_facturacion,
        direccion_envio=pedido.direccion_envio,
        notas=f'Generado desde pedido online #{pedido.numero}',
        usuario=pedido.modificado_por
    )
    
    # Cambiar estado de la venta a pagado
    VentaService.cambiar_estado_venta(venta, 'pagado', pedido.modificado_por)
    
    # Registrar el pago en la venta
    for pago_online in pedido.pagos.filter(estado='completado'):
        VentaService.registrar_pago(
            venta=venta,
            metodo=pago_online.metodo,
            monto=pago_online.monto,
            referencia=pago_online.referencia,
            estado='aprobado',
            datos_adicionales={},
            usuario=pedido.modificado_por
        )
    
    # Asociar la venta al pedido
    pedido.factura = venta
    pedido.save(update_fields=['factura'])