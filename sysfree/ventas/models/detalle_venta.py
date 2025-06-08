from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
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
        return f"{self.producto} x {self.cantidad:.2f}"
    
    def clean(self):
        """Valida los campos del detalle."""
        super().clean()
        if self.cantidad <= 0:
            raise ValidationError(_('La cantidad debe ser positiva.'))
        if self.precio_unitario < 0:
            raise ValidationError(_('El precio unitario no puede ser negativo.'))
        if self.descuento < 0:
            raise ValidationError(_('El descuento no puede ser negativo.'))
        if self.iva < 0:
            raise ValidationError(_('El IVA no puede ser negativo.'))
        if self.venta.tipo != 'proforma' and self.producto.es_inventariable and self.cantidad > self.producto.stock:
            raise ValidationError(_('La cantidad solicitada excede el stock disponible.'))
    
    def save(self, *args, **kwargs):
        """Calcula subtotal y total, y actualiza el stock si la venta no es proforma."""
        self.subtotal = self.cantidad * self.precio_unitario - self.descuento
        self.total = self.subtotal + self.iva
        super().save(*args, **kwargs)
        if self.venta.tipo != 'proforma' and self.venta.estado in ['emitida', 'pagada'] and self.producto.es_inventariable:
            self.producto.stock -= self.cantidad
            self.producto.save()