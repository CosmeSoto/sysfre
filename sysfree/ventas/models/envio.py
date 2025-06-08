from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from core.models import ModeloBase
from .venta import Venta


class Envio(ModeloBase):
    """Modelo para gestionar envíos de ventas."""
    
    ESTADO_CHOICES = (
        ('pendiente', _('Pendiente')),
        ('en_transito', _('En Tránsito')),
        ('entregado', _('Entregado')),
        ('devuelto', _('Devuelto')),
    )
    
    venta = models.ForeignKey(
        Venta,
        verbose_name=_('venta'),
        on_delete=models.CASCADE,
        related_name='envios'
    )
    transportista = models.CharField(_('transportista'), max_length=100)
    numero_seguimiento = models.CharField(_('número de seguimiento'), max_length=100, blank=True)
    fecha_envio = models.DateTimeField(_('fecha de envío'), null=True, blank=True)
    fecha_entrega = models.DateTimeField(_('fecha de entrega'), null=True, blank=True)
    estado = models.CharField(_('estado'), max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    notas = models.TextField(_('notas'), blank=True)
    
    class Meta:
        verbose_name = _('envío')
        verbose_name_plural = _('envíos')
        ordering = ['-fecha_envio']
    
    def __str__(self):
        return f"Envío {self.venta.numero} - {self.transportista}"
    
    def clean(self):
        """Valida los campos del envío."""
        super().clean()
        if self.fecha_entrega and self.fecha_envio and self.fecha_entrega < self.fecha_envio:
            raise ValidationError(_('La fecha de entrega no puede ser anterior a la fecha de envío.'))