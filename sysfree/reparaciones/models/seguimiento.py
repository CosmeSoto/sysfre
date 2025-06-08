from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from core.models import ModeloBase
from .reparacion import Reparacion

METODO_NOTIFICACION_CHOICES = (
    ('email', _('Email')),
    ('sms', _('SMS')),
    ('ninguno', _('Ninguno')),
)


class SeguimientoReparacion(ModeloBase):
    """Modelo para seguimiento de reparaciones."""
    
    reparacion = models.ForeignKey(
        Reparacion,
        verbose_name=_('reparación'),
        on_delete=models.CASCADE,
        related_name='seguimientos'
    )
    fecha = models.DateTimeField(_('fecha'), auto_now_add=True)
    estado_anterior = models.CharField(_('estado anterior'), max_length=20, blank=True)
    estado_nuevo = models.CharField(_('estado nuevo'), max_length=20)
    comentario = models.TextField(_('comentario'))
    
    # Campos para notificaciones
    notificado_cliente = models.BooleanField(_('notificado al cliente'), default=False)
    fecha_notificacion = models.DateTimeField(_('fecha de notificación'), null=True, blank=True)
    metodo_notificacion = models.CharField(
        _('método de notificación'),
        max_length=20,
        choices=METODO_NOTIFICACION_CHOICES,
        default='ninguno'
    )
    
    class Meta:
        verbose_name = _('seguimiento de reparación')
        verbose_name_plural = _('seguimientos de reparación')
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.reparacion} - {self.fecha} - {self.estado_nuevo}"
    
    def clean(self):
        super().clean()
        estados_validos = [choice[0] for choice in Reparacion.ESTADO_CHOICES]
        if self.estado_nuevo not in estados_validos:
            raise ValidationError({'estado_nuevo': _('Estado no válido para la reparación.')})