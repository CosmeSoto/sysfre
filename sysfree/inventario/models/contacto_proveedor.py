from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import ModeloBase
from .proveedor import Proveedor

class ContactoProveedor(ModeloBase):
    """Modelo para contactos múltiples de un proveedor."""
    
    proveedor = models.ForeignKey(
        Proveedor,
        verbose_name=_('proveedor'),
        on_delete=models.CASCADE,
        related_name='contactos'
    )
    nombre = models.CharField(_('nombre'), max_length=100)
    telefono = models.CharField(_('teléfono'), max_length=15, blank=True)
    email = models.EmailField(_('correo electrónico'), blank=True)
    cargo = models.CharField(_('cargo'), max_length=100, blank=True)
    
    class Meta:
        verbose_name = _('contacto de proveedor')
        verbose_name_plural = _('contactos de proveedores')
        ordering = ['proveedor', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.proveedor})"