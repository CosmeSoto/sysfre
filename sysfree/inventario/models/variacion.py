from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from core.models import ModeloBase
from .producto import Producto

class Variacion(ModeloBase):
    """Modelo para variaciones de productos (por ejemplo, colores, tallas)."""
    
    producto = models.ForeignKey(
        Producto,
        verbose_name=_('producto'),
        on_delete=models.CASCADE,
        related_name='variaciones'
    )
    atributo = models.CharField(_('atributo'), max_length=100)  # Ejemplo: "Color: Azul, Talla: M"
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
        """Valida que el stock y el precio no sean negativos."""
        if self.stock < 0:
            raise ValidationError(_('El stock no puede ser negativo.'))
        if self.precio_venta < 0:
            raise ValidationError(_('El precio de venta no puede ser negativo.'))
        super().clean()