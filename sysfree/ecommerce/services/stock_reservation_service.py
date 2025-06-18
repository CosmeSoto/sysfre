"""
Servicio para reservar stock temporalmente cuando un usuario agrega un producto al carrito.
"""
from django.utils import timezone
from ..models import ReservaStock

class StockReservationService:
    """Servicio para reservar stock temporalmente."""
    
    # Tiempo de expiración de la reserva en minutos
    TIEMPO_EXPIRACION = 30
    
    @staticmethod
    def reservar_stock(item_carrito, cantidad):
        """
        Reserva stock para un item del carrito.
        
        Args:
            item_carrito: Objeto ItemCarrito
            cantidad: Cantidad a reservar
            
        Returns:
            ReservaStock: Objeto ReservaStock creado
        """
        # Eliminar reservas anteriores para este item
        ReservaStock.objects.filter(item_carrito=item_carrito).delete()
        
        # Crear nueva reserva
        fecha_expiracion = timezone.now() + timezone.timedelta(minutes=StockReservationService.TIEMPO_EXPIRACION)
        reserva = ReservaStock.objects.create(
            item_carrito=item_carrito,
            cantidad=cantidad,
            fecha_expiracion=fecha_expiracion
        )
        
        return reserva
    
    @staticmethod
    def liberar_reserva(item_carrito):
        """
        Libera la reserva de stock para un item del carrito.
        
        Args:
            item_carrito: Objeto ItemCarrito
        """
        ReservaStock.objects.filter(item_carrito=item_carrito).delete()
    
    @staticmethod
    def limpiar_reservas_expiradas():
        """
        Limpia las reservas de stock expiradas.
        """
        ahora = timezone.now()
        ReservaStock.objects.filter(fecha_expiracion__lt=ahora).delete()
    
    @staticmethod
    def obtener_stock_disponible(producto):
        """
        Obtiene el stock disponible de un producto, teniendo en cuenta las reservas activas.
        
        Args:
            producto: Objeto Producto
            
        Returns:
            int: Stock disponible
        """
        # Obtener todas las reservas activas para este producto
        reservas = ReservaStock.objects.filter(
            item_carrito__producto=producto,
            activa=True,
            fecha_expiracion__gt=timezone.now()
        )
        
        # Calcular la cantidad total reservada
        cantidad_reservada = sum(reserva.cantidad for reserva in reservas)
        
        # Calcular el stock disponible
        stock_disponible = max(0, producto.stock - cantidad_reservada)
        
        return stock_disponible