from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from core.models import ModeloBase


class Pago(ModeloBase):
    """Modelo para pagos."""
    
    METODO_CHOICES = (
        ('efectivo', _('Efectivo')),
        ('tarjeta', _('Tarjeta de crédito/débito')),
        ('transferencia', _('Transferencia bancaria')),
        ('cheque', _('Cheque')),
        ('credito', _('Crédito')),
        ('otro', _('Otro')),
    )
    
    ESTADO_CHOICES = (
        ('pendiente', _('Pendiente')),
        ('aprobado', _('Aprobado')),
        ('rechazado', _('Rechazado')),
        ('anulado', _('Anulado')),
    )
    
    venta = models.ForeignKey(
        'Venta',
        verbose_name=_('venta'),
        on_delete=models.CASCADE,
        related_name='pagos'
    )
    fecha = models.DateTimeField(_('fecha'), auto_now_add=True)
    metodo = models.CharField(_('método'), max_length=15, choices=METODO_CHOICES)
    monto = models.DecimalField(_('monto'), max_digits=10, decimal_places=2)
    referencia = models.CharField(_('referencia'), max_length=100, blank=True)
    estado = models.CharField(_('estado'), max_length=10, choices=ESTADO_CHOICES, default='pendiente')
    
    numero_tarjeta = models.CharField(_('número de tarjeta'), max_length=19, blank=True)
    titular_tarjeta = models.CharField(_('titular de tarjeta'), max_length=100, blank=True)
    
    banco = models.CharField(_('banco'), max_length=100, blank=True)
    numero_cuenta = models.CharField(_('número de cuenta'), max_length=30, blank=True)
    
    numero_cheque = models.CharField(_('número de cheque'), max_length=30, blank=True)
    banco_cheque = models.CharField(_('banco del cheque'), max_length=100, blank=True)
    
    notas = models.TextField(_('notas'), blank=True)
    
    class Meta:
        verbose_name = _('pago')
        verbose_name_plural = _('pagos')
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.get_metodo_display()} - {self.monto:.2f}"
    
    def clean(self):
        """Valida los campos del pago."""
        super().clean()
        if self.monto <= 0:
            raise ValidationError(_('El monto debe ser positivo.'))
        if self.metodo == 'tarjeta' and (not self.numero_tarjeta or not self.titular_tarjeta):
            raise ValidationError(_('El número y titular de la tarjeta son requeridos para pagos con tarjeta.'))
        if self.metodo == 'transferencia' and (not self.banco or not self.numero_cuenta):
            raise ValidationError(_('El banco y número de cuenta son requeridos para transferencias.'))
        if self.metodo == 'cheque' and (not self.numero_cheque or not self.banco_cheque):
            raise ValidationError(_('El número y banco del cheque son requeridos para pagos con cheque.'))