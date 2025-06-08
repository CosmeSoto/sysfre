from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from core.models import ModeloBase
from .reparacion import Reparacion

class GarantiaReparacion(ModeloBase):
    """Modelo para gestionar garantías de reparaciones."""
    reparacion = models.ForeignKey(
        Reparacion,
        verbose_name=_('reparación'),
        on_delete=models.CASCADE,
        related_name='garantias'
    )
    fecha_inicio = models.DateField(_('fecha de inicio'))
    fecha_fin = models.DateField(_('fecha de fin'))
    condiciones = models.TextField(_('condiciones'))

    class Meta:
        verbose_name = _('garantía de reparación')
        verbose_name_plural = _('garantías de reparación')
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"Garantía {self.reparacion} - {self.fecha_fin}"
    
    def clean(self):
        """Valida que la fecha_fin no sea anterior a fecha_inicio."""
        if self.fecha_fin < self.fecha_inicio:
            raise ValidationError(_('La fecha de fin no puede ser anterior a la fecha de inicio.'))
        super().clean()