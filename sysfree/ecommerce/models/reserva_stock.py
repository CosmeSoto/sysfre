from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from core.models import ModeloBase
from .item_carrito import ItemCarrito

class ReservaStock(ModeloBase):
    """Modelo para reservas temporales de stock."""
    
    item_carrito = models.OneToOneField(
        ItemCarrito,
        verbose_name=_('item de carrito'),
        on_delete=models.CASCADE,
        related_name='reserva_stock'
    )
    cantidad = models.PositiveIntegerField(_('cantidad'))
    fecha_reserva = models.DateTimeField(_('fecha de reserva'), auto_now_add=True)
    fecha_expiracion = models.DateTimeField(_('fecha de expiración'))
    activa = models.BooleanField(_('activa'), default=True)
    
    class Meta:
        verbose_name = _('reserva de stock')
        verbose_name_plural = _('reservas de stock')
        ordering = ['-fecha_reserva']
    
    def __str__(self):
        return f"Reserva para {self.item_carrito} - {self.cantidad} unidades"
    
    def ha_expirado(self):
        """Verifica si la reserva ha expirado."""
        return timezone.now() > self.fecha_expiracion