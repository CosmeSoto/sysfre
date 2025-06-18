from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from core.models import ModeloBase


class Retencion(ModeloBase):
    """Modelo para retenciones."""
    
    TIPO_CHOICES = (
        ('iva', _('IVA')),
        ('renta', _('Renta')),
        ('otro', _('Otro')),
    )
    
    codigo = models.CharField(_('código'), max_length=10, unique=True)
    nombre = models.CharField(_('nombre'), max_length=100)
    descripcion = models.TextField(_('descripción'), blank=True)
    porcentaje = models.DecimalField(_('porcentaje'), max_digits=5, decimal_places=2)
    tipo = models.CharField(_('tipo'), max_length=10, choices=TIPO_CHOICES, default='renta')
    
    class Meta:
        verbose_name = _('retención')
        verbose_name_plural = _('retenciones')
        ordering = ['codigo']
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre} ({self.porcentaje}%)"
    
    def clean(self):
        """Valida que el porcentaje sea positivo."""
        if self.porcentaje < 0:
            raise ValidationError(_('El porcentaje no puede ser negativo.'))
        super().clean()