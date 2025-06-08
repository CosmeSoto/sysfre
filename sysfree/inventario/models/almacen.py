from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import ModeloBase

class Almacen(ModeloBase):
    """Modelo para almacenes o ubicaciones de inventario."""
    
    nombre = models.CharField(_('nombre'), max_length=100)
    direccion = models.TextField(_('dirección'), blank=True)
    responsable = models.CharField(_('responsable'), max_length=100, blank=True)
    activo = models.BooleanField(_('activo'), default=True)
    
    class Meta:
        verbose_name = _('almacén')
        verbose_name_plural = _('almacenes')
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre