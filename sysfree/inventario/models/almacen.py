from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import ModeloBase
from core.models import Sucursal

class Almacen(ModeloBase):
    """Modelo para almacenes o ubicaciones de inventario."""
    
    sucursal = models.ForeignKey(
        Sucursal,
        verbose_name=_('sucursal'),
        related_name='almacenes',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text=_('Sucursal asociada al almacén, si aplica.')
    )
    nombre = models.CharField(_('nombre'), max_length=100)
    direccion = models.TextField(_('dirección'), blank=True)
    responsable = models.CharField(_('responsable'), max_length=100, blank=True)
    activo = models.BooleanField(_('activo'), default=True)
    
    class Meta:
        verbose_name = _('almacén')
        verbose_name_plural = _('almacenes')
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.sucursal.nombre if self.sucursal else 'Sin sucursal'})"