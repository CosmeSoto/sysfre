from django.utils import timezone
from django.db.models import Sum, F, Q
from django.db import transaction
from ..models import Producto, MovimientoInventario, StockAlmacen, Almacen
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class InventarioService:
    """Servicio para gestionar operaciones de inventario."""
    
    @classmethod
    @transaction.atomic
    def registrar_entrada(cls, producto, cantidad, origen='compra', costo_unitario=None, 
                         proveedor=None, documento='', notas='', usuario=None, 
                         referencia_id=None, referencia_tipo='', almacen=None):
        """
        Registra una entrada de inventario.
        
        Args:
            producto (Producto): Producto al que se le registra la entrada
            cantidad (float): Cantidad a ingresar
            origen (str): Origen de la entrada (compra, ajuste_manual, etc.)
            costo_unitario (float): Costo unitario del producto
            proveedor (Proveedor): Proveedor del producto
            documento (str): Número de documento relacionado
            notas (str): Notas adicionales
            usuario (Usuario): Usuario que realiza la operación
            referencia_id (int): ID de la referencia (ej. ID de la compra)
            referencia_tipo (str): Tipo de referencia (ej. 'compra')
            almacen (Almacen): Almacén donde se registra la entrada
            
        Returns:
            MovimientoInventario: Movimiento creado
        """
        logger.info(f"Registrando entrada para producto {producto}, cantidad {cantidad}, almacén {almacen}")
        if not producto.es_inventariable:
            logger.warning(f"Producto {producto} no es inventariable")
            return None
        if not almacen:
            logger.error("El almacén es obligatorio")
            raise ValueError("El almacén es obligatorio")
        if cantidad <= 0:
            logger.error("La cantidad debe ser mayor que cero")
            raise ValueError("La cantidad debe ser mayor que cero")
        if costo_unitario is None or costo_unitario <= 0:
            logger.error("El costo unitario debe ser mayor que cero")
            raise ValueError("El costo unitario debe ser mayor que cero")
            
        # Crear o actualizar stock en almacén
        stock_almacen, _ = StockAlmacen.objects.get_or_create(
            producto=producto,
            almacen=almacen,
            defaults={'cantidad': Decimal('0.00')}
        )
        
        movimiento = MovimientoInventario(
            tipo='entrada',
            origen=origen,
            producto=producto,
            cantidad=Decimal(cantidad),
            stock_anterior=stock_almacen.cantidad,
            stock_nuevo=stock_almacen.cantidad + Decimal(cantidad),
            costo_unitario=Decimal(costo_unitario),
            proveedor=proveedor,
            documento=documento,
            notas=notas,
            referencia_id=referencia_id,
            referencia_tipo=referencia_tipo,
            almacen=almacen
        )
        
        if usuario:
            movimiento.creado_por = usuario
        
        try:
            movimiento.clean()  # Ejecutar validaciones del modelo
            movimiento.save()
            logger.info(f"Movimiento de entrada creado: {movimiento}")
        except Exception as e:
            logger.error(f"Error al guardar movimiento de entrada: {str(e)}")
            raise
        
        return movimiento
    
    @classmethod
    @transaction.atomic
    def registrar_salida(cls, producto, cantidad, origen='venta', 
                        documento='', notas='', usuario=None,
                        referencia_id=None, referencia_tipo='', almacen=None):
        """
        Registra una salida de inventario.
        
        Args:
            producto (Producto): Producto al que se le registra la salida
            cantidad (float): Cantidad a retirar
            origen (str): Origen de la salida (venta, ajuste_manual, etc.)
            documento (str): Número de documento relacionado
            notas (str): Notas adicionales
            usuario (Usuario): Usuario que realiza la operación
            referencia_id (int): ID de la referencia (ej. ID de la venta)
            referencia_tipo (str): Tipo de referencia (ej. 'venta')
            almacen (Almacen): Almacén donde se registra la salida
            
        Returns:
            MovimientoInventario: Movimiento creado
        """
        logger.info(f"Registrando salida para producto {producto}, cantidad {cantidad}, almacén {almacen}")
        if not producto.es_inventariable:
            logger.warning(f"Producto {producto} no es inventariable")
            return None
        if not almacen:
            logger.error("El almacén es obligatorio")
            raise ValueError("El almacén es obligatorio")
        if cantidad <= 0:
            logger.error("La cantidad debe ser mayor que cero")
            raise ValueError("La cantidad debe ser mayor que cero")
            
        # Verificar stock disponible
        stock_almacen = StockAlmacen.objects.filter(producto=producto, almacen=almacen).first()
        if not stock_almacen or stock_almacen.cantidad < cantidad:
            logger.error(f"Stock insuficiente para producto {producto} en almacén {almacen}")
            raise ValueError(f"Stock insuficiente para el producto {producto.nombre} en el almacén {almacen.nombre}")
            
        movimiento = MovimientoInventario(
            tipo='salida',
            origen=origen,
            producto=producto,
            cantidad=Decimal(cantidad),
            stock_anterior=stock_almacen.cantidad,
            stock_nuevo=stock_almacen.cantidad - Decimal(cantidad),
            documento=documento,
            notas=notas,
            referencia_id=referencia_id,
            referencia_tipo=referencia_tipo,
            almacen=almacen
        )
        
        if usuario:
            movimiento.creado_por = usuario
        
        try:
            movimiento.clean()  # Ejecutar validaciones del modelo
            movimiento.save()
            logger.info(f"Movimiento de salida creado: {movimiento}")
        except Exception as e:
            logger.error(f"Error al guardar movimiento de salida: {str(e)}")
            raise
        
        return movimiento
    
    @classmethod
    @transaction.atomic
    def ajustar_inventario(cls, producto, cantidad_nueva, notas='', usuario=None, almacen=None):
        """
        Ajusta el inventario a una cantidad específica.
        
        Args:
            producto (Producto): Producto a ajustar
            cantidad_nueva (float): Nueva cantidad de stock
            notas (str): Notas adicionales
            usuario (Usuario): Usuario que realiza la operación
            almacen (Almacen): Almacén donde se realiza el ajuste
            
        Returns:
            MovimientoInventario: Movimiento creado
        """
        logger.info(f"Ajustando inventario para producto {producto}, cantidad nueva {cantidad_nueva}, almacén {almacen}")
        if not producto.es_inventariable:
            logger.warning(f"Producto {producto} no es inventariable")
            return None
        if not almacen:
            logger.error("El almacén es obligatorio")
            raise ValueError("El almacén es obligatorio")
        if cantidad_nueva < 0:
            logger.error("La cantidad nueva no puede ser negativa")
            raise ValueError("La cantidad nueva no puede ser negativa")
            
        stock_almacen = StockAlmacen.objects.filter(producto=producto, almacen=almacen).first()
        stock_anterior = stock_almacen.cantidad if stock_almacen else Decimal('0.00')
        
        movimiento = MovimientoInventario(
            tipo='ajuste',
            origen='ajuste_manual',
            producto=producto,
            cantidad=Decimal(cantidad_nueva) - stock_anterior,
            stock_anterior=stock_anterior,
            stock_nuevo=Decimal(cantidad_nueva),
            notas=notas,
            almacen=almacen
        )
        
        if usuario:
            movimiento.creado_por = usuario
        
        try:
            movimiento.clean()  # Ejecutar validaciones del modelo
            movimiento.save()
            logger.info(f"Movimiento de ajuste creado: {movimiento}")
        except Exception as e:
            logger.error(f"Error al guardar movimiento de ajuste: {str(e)}")
            raise
        
        return movimiento
    
    @classmethod
    def obtener_productos_bajo_stock(cls):
        """
        Obtiene los productos que están por debajo del stock mínimo.
        
        Returns:
            QuerySet: Productos con stock bajo
        """
        return Producto.objects.filter(
            es_inventariable=True,
            activo=True,
            stock__lt=F('stock_minimo')
        ).order_by('nombre')
    
    @classmethod
    def obtener_movimientos_producto(cls, producto, fecha_inicio=None, fecha_fin=None):
        """
        Obtiene los movimientos de un producto en un rango de fechas.
        
        Args:
            producto (Producto): Producto a consultar
            fecha_inicio (date): Fecha de inicio del rango
            fecha_fin (date): Fecha de fin del rango
            
        Returns:
            QuerySet: Movimientos del producto
        """
        query = Q(producto=producto)
        
        if fecha_inicio:
            query &= Q(fecha__gte=fecha_inicio)
        
        if fecha_fin:
            query &= Q(fecha__lte=fecha_fin)
            
        return MovimientoInventario.objects.filter(query).order_by('-fecha')