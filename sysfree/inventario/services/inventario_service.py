from django.utils import timezone
from django.db.models import Sum, F, Q
from ..models import Producto, MovimientoInventario


class InventarioService:
    """Servicio para gestionar operaciones de inventario."""
    
    @classmethod
    def registrar_entrada(cls, producto, cantidad, origen='compra', costo_unitario=None, 
                         proveedor=None, documento='', notas='', usuario=None, 
                         referencia_id=None, referencia_tipo=''):
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
            
        Returns:
            MovimientoInventario: Movimiento creado
        """
        if not producto.es_inventariable:
            return None
            
        movimiento = MovimientoInventario(
            tipo='entrada',
            origen=origen,
            producto=producto,
            cantidad=cantidad,
            stock_anterior=producto.stock, # Asignar stock_anterior
            costo_unitario=costo_unitario,
            proveedor=proveedor,
            documento=documento,
            notas=notas,
            referencia_id=referencia_id,
            referencia_tipo=referencia_tipo
        )
        
        if usuario:
            movimiento.creado_por = usuario
        
        producto.stock += cantidad # Actualizar stock del producto
        movimiento.stock_nuevo = producto.stock # Asignar stock_nuevo
        producto.save(update_fields=['stock', 'fecha_ultimo_movimiento'])
        movimiento.save()
        return movimiento
    
    @classmethod
    def registrar_salida(cls, producto, cantidad, origen='venta', 
                        documento='', notas='', usuario=None,
                        referencia_id=None, referencia_tipo=''):
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
            
        Returns:
            MovimientoInventario: Movimiento creado
        """
        if not producto.es_inventariable:
            return None
            
        # Verificar si hay suficiente stock
        if producto.stock < cantidad:
            raise ValueError(f"Stock insuficiente para el producto {producto.nombre}")
            
        movimiento = MovimientoInventario(
            tipo='salida',
            origen=origen,
            producto=producto,
            cantidad=cantidad,
            stock_anterior=producto.stock, # Asignar stock_anterior
            documento=documento,
            notas=notas,
            referencia_id=referencia_id,
            referencia_tipo=referencia_tipo
        )
        
        if usuario:
            movimiento.creado_por = usuario

        producto.stock -= cantidad # Actualizar stock del producto
        movimiento.stock_nuevo = producto.stock # Asignar stock_nuevo
        producto.save(update_fields=['stock', 'fecha_ultimo_movimiento'])
        movimiento.save()
        return movimiento
    
    @classmethod
    def ajustar_inventario(cls, producto, cantidad_nueva, notas='', usuario=None):
        """
        Ajusta el inventario a una cantidad específica.
        
        Args:
            producto (Producto): Producto a ajustar
            cantidad_nueva (float): Nueva cantidad de stock
            notas (str): Notas adicionales
            usuario (Usuario): Usuario que realiza la operación
            
        Returns:
            MovimientoInventario: Movimiento creado
        """
        if not producto.es_inventariable:
            return None
            
        movimiento = MovimientoInventario(
            tipo='ajuste',
            origen='ajuste_manual',
            producto=producto,
            cantidad=cantidad_nueva - producto.stock, # La cantidad del movimiento es la diferencia
            stock_anterior=producto.stock,
            notas=notas
        )
        
        if usuario:
            movimiento.creado_por = usuario

        producto.stock = cantidad_nueva # Actualizar stock del producto
        movimiento.stock_nuevo = producto.stock # Asignar stock_nuevo
        producto.save(update_fields=['stock', 'fecha_ultimo_movimiento'])
        movimiento.save()
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