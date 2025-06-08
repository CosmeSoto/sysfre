from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
from core.models import ModeloBase
from clientes.models import Cliente
from .reparacion import Reparacion

class CitaServicio(ModeloBase):
    """Modelo para gestionar citas de clientes para reparaciones o diagnósticos."""
    cliente = models.ForeignKey(
        Cliente,
        verbose_name=_('cliente'),
        on_delete=models.PROTECT,
        related_name='citas'
    )
    fecha_hora = models.DateTimeField(_('fecha y hora'))
    tipo_equipo = models.CharField(_('tipo de equipo'), max_length=100)
    estado = models.CharField(
        _('estado'),
        max_length=20,
        choices=(
            ('pendiente', _('Pendiente')),
            ('confirmada', _('Confirmada')),
            ('cancelada', _('Cancelada')),
        ),
        default='pendiente'
    )
    reparacion = models.ForeignKey(
        Reparacion,
        verbose_name=_('reparación'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='citas'
    )

    class Meta:
        verbose_name = _('cita de servicio')
        verbose_name_plural = _('citas de servicio')
        ordering = ['-fecha_hora']

    def __str__(self):
        return f"Cita {self.cliente} - {self.fecha_hora}"
    
    def clean(self):
        """Valida que la fecha_hora no sea en el pasado."""
        if self.fecha_hora < timezone.now():
            raise ValidationError(_('La fecha y hora no pueden estar en el pasado.'))
        super().clean()