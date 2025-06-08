from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from core.models import ModeloBase


class Impuesto(ModeloBase):
    """Modelo para tipos de impuestos."""
    
    nombre = models.CharField(_('nombre'), max_length=100)
    codigo = models.CharField(_('código'), max_length=20, unique=True)
    porcentaje = models.DecimalField(_('porcentaje'), max_digits=5, decimal_places=2)
    descripcion = models.TextField(_('descripción'), blank=True)
    
    class Meta:
        verbose_name = _('impuesto')
        verbose_name_plural = _('impuestos')
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.porcentaje:.2f}%)"
    
    def clean(self):
        """Valida que el porcentaje no sea negativo."""
        if self.porcentaje < 0:
            raise ValidationError(_('El porcentaje no puede ser negativo.'))
        super().clean()