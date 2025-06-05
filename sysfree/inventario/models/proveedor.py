from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import ModeloBase


class Proveedor(ModeloBase):
    """Modelo para proveedores de productos."""
    
    nombre = models.CharField(_('nombre'), max_length=200)
    ruc = models.CharField(_('RUC'), max_length=13, unique=True)
    direccion = models.TextField(_('dirección'), blank=True)
    telefono = models.CharField(_('teléfono'), max_length=15, blank=True)
    email = models.EmailField(_('correo electrónico'), blank=True)
    sitio_web = models.URLField(_('sitio web'), blank=True)
    contacto_nombre = models.CharField(_('nombre de contacto'), max_length=100, blank=True)
    contacto_telefono = models.CharField(_('teléfono de contacto'), max_length=15, blank=True)
    contacto_email = models.EmailField(_('correo de contacto'), blank=True)
    notas = models.TextField(_('notas'), blank=True)
    
    # Campos para control de crédito
    dias_credito = models.PositiveIntegerField(_('días de crédito'), default=0)
    limite_credito = models.DecimalField(_('límite de crédito'), max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = _('proveedor')
        verbose_name_plural = _('proveedores')
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre