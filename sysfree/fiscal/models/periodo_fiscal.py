from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import ModeloBase


class PeriodoFiscal(ModeloBase):
    """Modelo para periodos fiscales."""
    
    ESTADO_CHOICES = (
        ('abierto', _('Abierto')),
        ('cerrado', _('Cerrado')),
    )
    
    nombre = models.CharField(_('nombre'), max_length=100)
    fecha_inicio = models.DateField(_('fecha de inicio'))
    fecha_fin = models.DateField(_('fecha de fin'))
    estado = models.CharField(_('estado'), max_length=10, choices=ESTADO_CHOICES, default='abierto')
    notas = models.TextField(_('notas'), blank=True)
    
    class Meta:
        verbose_name = _('periodo fiscal')
        verbose_name_plural = _('periodos fiscales')
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        return self.nombre
    
    @property
    def esta_activo(self):
        """Indica si el periodo fiscal está activo."""
        from django.utils import timezone
        today = timezone.now().date()
        return self.fecha_inicio <= today <= self.fecha_fin and self.estado == 'abierto'