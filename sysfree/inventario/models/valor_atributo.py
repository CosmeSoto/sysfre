from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from core.models import ModeloBase
from .atributo import Atributo
from decimal import Decimal


class ValorAtributo(ModeloBase):
    """Modelo para valores específicos de atributos (ej. Rojo, XL, Algodón)."""
    
    atributo = models.ForeignKey(
        Atributo,
        verbose_name=_('atributo'),
        on_delete=models.CASCADE,
        related_name='valores'
    )
    valor = models.CharField(_('valor'), max_length=100)
    codigo = models.CharField(_('código'), max_length=50, blank=True)
    precio_adicional = models.DecimalField(
        _('precio adicional'), 
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text=_('Precio adicional que se suma al precio base del producto')
    )
    imagen = models.ImageField(_('imagen'), upload_to='valores_atributos/', blank=True, null=True)
    productos = models.ManyToManyField(
        'Producto',
        verbose_name=_('productos'),
        related_name='valores_atributos',
        blank=True,
        help_text=_('Productos que pueden usar este valor de atributo')
    )
    activo = models.BooleanField(_('activo'), default=True, help_text=_('Indica si el valor está activo'))
    
    class Meta:
        verbose_name = _('valor de atributo')
        verbose_name_plural = _('valores de atributos')
        ordering = ['atributo', 'valor']
        unique_together = ['atributo', 'valor']
        indexes = [
            models.Index(fields=['atributo', 'valor']),
        ]
    
    def __str__(self):
        return f"{self.atributo.nombre}: {self.valor}"
    
    def clean(self):
        if self.precio_adicional is not None and self.precio_adicional < 0:
            raise ValidationError(_('El precio adicional no puede ser negativo.'))
        super().clean()