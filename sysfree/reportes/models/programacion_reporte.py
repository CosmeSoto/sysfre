from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from core.models import ModeloBase
from .reporte import Reporte


class ProgramacionReporte(ModeloBase):
    """Modelo para programar la ejecución automática de reportes."""
    
    FRECUENCIA_CHOICES = (
        ('diaria', _('Diaria')),
        ('semanal', _('Semanal')),
        ('mensual', _('Mensual')),
        ('trimestral', _('Trimestral')),
        ('anual', _('Anual')),
    )
    
    DIA_SEMANA_CHOICES = (
        (0, _('Lunes')),
        (1, _('Martes')),
        (2, _('Miércoles')),
        (3, _('Jueves')),
        (4, _('Viernes')),
        (5, _('Sábado')),
        (6, _('Domingo')),
    )
    
    reporte = models.ForeignKey(
        Reporte,
        verbose_name=_('reporte'),
        on_delete=models.CASCADE,
        related_name='programaciones'
    )
    nombre = models.CharField(_('nombre'), max_length=100)
    frecuencia = models.CharField(_('frecuencia'), max_length=10, choices=FRECUENCIA_CHOICES)
    hora = models.TimeField(_('hora'))
    dia_semana = models.IntegerField(_('día de la semana'), choices=DIA_SEMANA_CHOICES, null=True, blank=True)
    dia_mes = models.IntegerField(_('día del mes'), null=True, blank=True)
    mes = models.IntegerField(_('mes'), null=True, blank=True)
    parametros = models.JSONField(_('parámetros'), default=dict, blank=True)
    destinatarios = models.TextField(_('destinatarios'), help_text=_('Correos electrónicos separados por comas'))
    asunto = models.CharField(_('asunto'), max_length=200)
    mensaje = models.TextField(_('mensaje'), blank=True)
    ultima_ejecucion = models.DateTimeField(_('última ejecución'), null=True, blank=True)
    proxima_ejecucion = models.DateTimeField(_('próxima ejecución'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('programación de reporte')
        verbose_name_plural = _('programaciones de reportes')
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} - {self.reporte}"
    
    def clean(self):
        """Valida los campos de la programación."""
        super().clean()
        if self.frecuencia == 'semanal' and self.dia_semana is None:
            raise ValidationError(_('El día de la semana es requerido para frecuencias semanales.'))
        if self.frecuencia == 'mensual' and self.dia_mes is None:
            raise ValidationError(_('El día del mes es requerido para frecuencias mensuales.'))
        if self.destinatarios:
            emails = [email.strip() for email in self.destinatarios.split(',')]
            for email in emails:
                try:
                    validate_email(email)
                except ValidationError:
                    raise ValidationError(_(f'El correo "{email}" no es válido.'))