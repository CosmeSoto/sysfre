"""
Servicio para validar el stock de productos antes de procesar un pedido.
"""
from django.utils.translation import gettext_lazy as _
from ..models import Carrito, ItemCarrito

class StockValidationService:
    """Servicio para validar el stock de productos."""
    
    @staticmethod
    def validar_stock_carrito(carrito):
        """
        Valida que haya suficiente stock para todos los productos en el carrito.
        
        Args:
            carrito: Objeto Carrito
            
        Returns:
            tuple: (bool, list) - (stock_valido, productos_sin_stock)
        """
        productos_sin_stock = []
        
        for item in carrito.items.all():
            if not item.es_servicio and item.producto and item.producto.es_inventariable:
                if item.producto.stock < item.cantidad:
                    productos_sin_stock.append({
                        'producto': item.producto,
                        'stock_actual': item.producto.stock,
                        'cantidad_solicitada': item.cantidad
                    })
        
        return len(productos_sin_stock) == 0, productos_sin_stock
    
    @staticmethod
    def validar_stock_producto(producto, cantidad):
        """
        Valida que haya suficiente stock para un producto específico.
        
        Args:
            producto: Objeto Producto
            cantidad: Cantidad solicitada
            
        Returns:
            bool: True si hay suficiente stock, False en caso contrario
        """
        if not producto.es_inventariable:
            return True
            
        return producto.stock >= cantidad