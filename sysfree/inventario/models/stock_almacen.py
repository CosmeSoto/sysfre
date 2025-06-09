from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from core.models import ModeloBase
from .producto import Producto
from .almacen import Almacen
from decimal import Decimal
from django.db.models import Sum

class StockAlmacen(ModeloBase):
    """Modelo para el stock de un producto en un almacén específico."""
    
    producto = models.ForeignKey(
        Producto,
        verbose_name=_('producto'),
        on_delete=models.CASCADE,
        related_name='stocks'
    )
    almacen = models.ForeignKey(
        Almacen,
        verbose_name=_('almacén'),
        on_delete=models.CASCADE,
        related_name='stocks'
    )
    cantidad = models.DecimalField(_('cantidad'), max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = _('stock por almacén')
        verbose_name_plural = _('stocks por almacén')
        unique_together = ['producto', 'almacen']
        ordering = ['producto', 'almacen']
    
    def __str__(self):
        return f"{self.producto} - {self.almacen} - {self.cantidad}"
    
    def clean(self):
        if self.cantidad is None:
            raise ValidationError(_('La cantidad no puede ser nula.'))
        if self.cantidad < 0:
            raise ValidationError(_('La cantidad no puede ser negativa.'))
        super().clean()
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_producto_stock()

    def delete(self, *args, **kwargs):
        producto = self.producto
        super().delete(*args, **kwargs)
        self.update_producto_stock(producto)

    def update_producto_stock(self, producto=None):
        if producto is None:
            producto = self.producto
        total_stock = StockAlmacen.objects.filter(producto=producto).aggregate(
            total=Sum('cantidad')
        )['total'] or Decimal('0.00')
        if not producto.variaciones.exists():
            producto.stock = total_stock
            producto.save(update_fields=['stock'])