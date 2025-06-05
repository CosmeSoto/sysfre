from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import ModeloBase
from inventario.models import Producto
from .venta import Venta


class DetalleVenta(ModeloBase):
    """Modelo para detalles de venta."""
    
    venta = models.ForeignKey(
        Venta,
        verbose_name=_('venta'),
        on_delete=models.CASCADE,
        related_name='detalles'
    )
    producto = models.ForeignKey(
        Producto,
        verbose_name=_('producto'),
        on_delete=models.PROTECT,
        related_name='detalles_venta'
    )
    cantidad = models.DecimalField(_('cantidad'), max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(_('precio unitario'), max_digits=10, decimal_places=2)
    descuento = models.DecimalField(_('descuento'), max_digits=10, decimal_places=2, default=0)
    iva = models.DecimalField(_('IVA'), max_digits=10, decimal_places=2, default=0)
    subtotal = models.DecimalField(_('subtotal'), max_digits=10, decimal_places=2)
    total = models.DecimalField(_('total'), max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = _('detalle de venta')
        verbose_name_plural = _('detalles de venta')
        ordering = ['id']
    
    def __str__(self):
        return f"{self.producto} x {self.cantidad}"
    
    def save(self, *args, **kwargs):
        """Sobrescribe el método save para calcular subtotal y total."""
        self.subtotal = self.cantidad * self.precio_unitario - self.descuento
        self.total = self.subtotal + self.iva
        super().save(*args, **kwargs)