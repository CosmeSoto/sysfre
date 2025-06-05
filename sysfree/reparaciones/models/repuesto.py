from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import ModeloBase
from inventario.models import Producto
from .reparacion import Reparacion


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
    
    class Meta:
        verbose_name = _('repuesto de reparación')
        verbose_name_plural = _('repuestos de reparación')
        ordering = ['id']
    
    def __str__(self):
        return f"{self.producto} x {self.cantidad} - {self.reparacion}"
    
    def save(self, *args, **kwargs):
        """Sobrescribe el método save para calcular el subtotal."""
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)