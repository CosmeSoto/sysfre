from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from core.models import ModeloBase
from inventario.models import Producto
from .reparacion import Reparacion
from core.services import IVAService


class RepuestoReparacion(ModeloBase):
    """Modelo para repuestos utilizados en reparaciones."""
    
    reparacion = models.ForeignKey(
        Reparacion,
        verbose_name=_('reparación'),
        on_delete=models.CASCADE,
        related_name='repuestos'
    )
    producto = models.ForeignKey(
        Producto,
        verbose_name=_('producto'),
        on_delete=models.PROTECT,
        related_name='reparaciones'
    )
    cantidad = models.DecimalField(_('cantidad'), max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(_('precio unitario'), max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(_('subtotal'), max_digits=10, decimal_places=2)
    impuesto_unitario = models.DecimalField(_('impuesto unitario'), max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = _('repuesto de reparación')
        verbose_name_plural = _('repuestos de reparación')
        ordering = ['id']
    
    def __str__(self):
        return f"{self.producto} x {self.cantidad:.2f} - {self.reparacion}"
    
    def clean(self):
        super().clean()
        if self.cantidad < 0:
            raise ValidationError(_('La cantidad no puede ser negativa.'))
        if self.precio_unitario < 0:
            raise ValidationError(_('El precio unitario no puede ser negativo.'))
        if getattr(self.producto, 'es_inventariable', False) and self.cantidad > getattr(self.producto, 'stock', 0):
            raise ValidationError(_('La cantidad solicitada excede el stock disponible.'))
    
    def save(self, *args, **kwargs):
        """Sobrescribe el método save para calcular el subtotal y el impuesto unitario."""
        self.subtotal = self.cantidad * self.precio_unitario

        # Calcular el impuesto unitario usando el tipo_iva del producto
        tipo_iva = getattr(self.producto, 'tipo_iva', None)
        tipo_iva = tipo_iva or IVAService.get_default()
        monto_iva, _ = IVAService.calcular_iva(self.precio_unitario, tipo_iva)
        self.impuesto_unitario = monto_iva

        super().save(*args, **kwargs)