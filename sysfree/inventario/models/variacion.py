from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from core.models import ModeloBase
from .producto import Producto
from .stock_almacen import StockAlmacen
from decimal import Decimal
from django.db.models import Sum
from django.db.models.signals import post_delete
from django.dispatch import receiver

class Variacion(ModeloBase):
    """Modelo para variaciones de productos (por ejemplo, colores, tallas)."""
    
    producto = models.ForeignKey(
        Producto,
        verbose_name=_('producto'),
        on_delete=models.CASCADE,
        related_name='variaciones'
    )
    atributo = models.CharField(_('atributo'), max_length=100)
    codigo = models.CharField(_('código'), max_length=50, unique=True)
    stock = models.DecimalField(_('stock'), max_digits=10, decimal_places=2, default=0)
    precio_venta = models.DecimalField(_('precio de venta'), max_digits=10, decimal_places=2)
    imagen = models.ImageField(_('imagen'), upload_to='variaciones/', blank=True, null=True)
    
    class Meta:
        verbose_name = _('variación')
        verbose_name_plural = _('variaciones')
        ordering = ['producto', 'atributo']
    
    def __str__(self):
        return f"{self.producto} - {self.atributo}"
    
    def clean(self):
        if self.stock is None:
            raise ValidationError(_('La cantidad no puede ser nula.'))
        if self.stock < 0:
            raise ValidationError(_('El stock no puede ser negativo.'))
        if self.precio_venta is None:
            raise ValidationError(_('El precio de venta no puede ser nulo.'))
        if self.precio_venta < 0:
            raise ValidationError(_('El precio de venta no puede ser negativo.'))
        super().clean()
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.producto.variaciones.exists():
            total_stock = self.producto.variaciones.aggregate(
                total=Sum('stock')
            )['total'] or Decimal('0.00')
            self.producto.stock = total_stock
            self.producto.save(update_fields=['stock'])

@receiver(post_delete, sender=Variacion)
def update_producto_stock_on_delete(sender, instance, **kwargs):
    """Actualiza el stock del producto cuando se elimina una variación."""
    producto = instance.producto
    total_stock = producto.variaciones.aggregate(
        total=Sum('stock')
    )['total'] or Decimal('0.00')
    if not producto.variaciones.exists():
        total_stock = StockAlmacen.objects.filter(producto=producto).aggregate(
            total=Sum('cantidad')
        )['total'] or Decimal('0.00')
    producto.stock = total_stock
    producto.save(update_fields=['stock'])