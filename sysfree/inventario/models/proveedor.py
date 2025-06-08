from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from core.models import ModeloBase

class Proveedor(ModeloBase):
    """Modelo para proveedores de productos."""
    
    nombre = models.CharField(_('nombre'), max_length=200)
    ruc = models.CharField(_('RUC'), max_length=13, unique=True)
    direccion = models.TextField(_('dirección'), blank=True)
    telefono = models.CharField(_('teléfono'), max_length=15, blank=True)
    email = models.EmailField(_('correo electrónico'), blank=True)
    sitio_web = models.URLField(_('sitio web'), blank=True)
    notas = models.TextField(_('notas'), blank=True)
    
    dias_credito = models.PositiveIntegerField(_('días de crédito'), default=0)
    limite_credito = models.DecimalField(_('límite de crédito'), max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(
        _('estado'),
        max_length=10,
        choices=(('activo', _('Activo')), ('inactivo', _('Inactivo'))),
        default='activo'
    )
    
    class Meta:
        verbose_name = _('proveedor')
        verbose_name_plural = _('proveedores')
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre
    
    def clean(self):
        """Valida que el límite de crédito no sea negativo."""
        if self.limite_credito < 0:
            raise ValidationError(_('El límite de crédito no puede ser negativo.'))
        super().clean()