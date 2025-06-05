from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import ModeloBase
from .pedido import Pedido


class PagoOnline(ModeloBase):
    """Modelo para pagos online de pedidos."""
    
    METODO_CHOICES = (
        ('tarjeta', _('Tarjeta de crédito/débito')),
        ('paypal', _('PayPal')),
        ('transferencia', _('Transferencia bancaria')),
        ('efectivo', _('Efectivo contra entrega')),
        ('otro', _('Otro')),
    )
    
    ESTADO_CHOICES = (
        ('pendiente', _('Pendiente')),
        ('procesando', _('Procesando')),
        ('completado', _('Completado')),
        ('fallido', _('Fallido')),
        ('reembolsado', _('Reembolsado')),
    )
    
    pedido = models.ForeignKey(
        Pedido,
        verbose_name=_('pedido'),
        on_delete=models.CASCADE,
        related_name='pagos'
    )
    metodo = models.CharField(_('método de pago'), max_length=15, choices=METODO_CHOICES)
    monto = models.DecimalField(_('monto'), max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(_('fecha'), auto_now_add=True)
    estado = models.CharField(_('estado'), max_length=15, choices=ESTADO_CHOICES, default='pendiente')
    referencia = models.CharField(_('referencia'), max_length=100, blank=True)
    
    # Campos para pasarela de pago
    pasarela_id = models.CharField(_('ID de transacción'), max_length=100, blank=True)
    pasarela_respuesta = models.JSONField(_('respuesta de pasarela'), default=dict, blank=True)
    
    class Meta:
        verbose_name = _('pago online')
        verbose_name_plural = _('pagos online')
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.get_metodo_display()} - {self.monto} - {self.pedido}"