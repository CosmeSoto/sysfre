from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from core.models import ModeloBase
from .reporte import Reporte
from .programacion_reporte import ProgramacionReporte


class HistorialReporte(ModeloBase):
    """Modelo para registrar el historial de ejecución de reportes."""
    
    ESTADO_CHOICES = (
        ('exito', _('Éxito')),
        ('error', _('Error')),
    )
    
    reporte = models.ForeignKey(
        Reporte,
        verbose_name=_('reporte'),
        on_delete=models.CASCADE,
        related_name='historial'
    )
    programacion = models.ForeignKey(
        ProgramacionReporte,
        verbose_name=_('programación'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='historial'
    )
    fecha_ejecucion = models.DateTimeField(_('fecha de ejecución'), auto_now_add=True)
    duracion = models.IntegerField(_('duración (segundos)'), null=True, blank=True)
    estado = models.CharField(_('estado'), max_length=5, choices=ESTADO_CHOICES)
    mensaje_error = models.TextField(_('mensaje de error'), blank=True)
    parametros = models.JSONField(_('parámetros'), default=dict, blank=True)
    archivo = models.FileField(_('archivo'), upload_to='reportes/', null=True, blank=True)
    
    class Meta:
        verbose_name = _('historial de reporte')
        verbose_name_plural = _('historial de reportes')
        ordering = ['-fecha_ejecucion']
    
    def __str__(self):
        return f"{self.reporte} - {self.fecha_ejecucion}"
    
    def clean(self):
        """Valida que la duración no sea negativa."""
        super().clean()
        if self.duracion is not None and self.duracion < 0:
            raise ValidationError(_('La duración no puede ser negativa.'))