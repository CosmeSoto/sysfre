from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from core.models import ModeloBase
from core.services import IVAService
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
    tipo_iva = models.ForeignKey(
        'core.TipoIVA',
        verbose_name=_('tipo de IVA'),
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='detalles_venta'
    )
    subtotal = models.DecimalField(_('subtotal'), max_digits=10, decimal_places=2)
    iva = models.DecimalField(_('IVA'), max_digits=10, decimal_places=2, default=0)
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
        if self.venta.tipo != 'proforma' and self.producto.es_inventariable and self.cantidad > self.producto.stock:
            raise ValidationError(_('La cantidad solicitada excede el stock disponible.'))
    
    def save(self, *args, **kwargs):
        """Calcula subtotal, IVA, total y actualiza el stock si la venta no es proforma."""
        # Calcular subtotal
        self.subtotal = self.cantidad * self.precio_unitario - self.descuento
        
        # Obtener tipo_iva del producto o el predeterminado
        if not self.tipo_iva:
            self.tipo_iva = getattr(self.producto, 'tipo_iva', None) or IVAService.get_default()
        
        # Calcular IVA y total usando IVAService
        self.iva, self.total = IVAService.calcular_iva(self.subtotal, self.tipo_iva)
        
        # Guardar el detalle
        super().save(*args, **kwargs)
        
        # Actualizar stock si aplica
        if self.venta.tipo != 'proforma' and self.venta.estado in ['emitida', 'pagada'] and self.producto.es_inventariable:
            self.producto.stock -= self.cantidad
            self.producto.save()