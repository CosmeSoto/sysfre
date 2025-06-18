from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import ModeloBase
from .producto import Producto

class AlertaStock(ModeloBase):
    """Modelo para alertas de stock bajo."""
    
    ESTADO_CHOICES = (
        ('pendiente', _('Pendiente')),
        ('en_proceso', _('En proceso')),
        ('resuelta', _('Resuelta')),
        ('ignorada', _('Ignorada')),
    )
    
    producto = models.ForeignKey(
        Producto,
        verbose_name=_('producto'),
        on_delete=models.CASCADE,
        related_name='alertas_stock'
    )
    stock_actual = models.DecimalField(_('stock actual'), max_digits=10, decimal_places=2)
    stock_minimo = models.DecimalField(_('stock mínimo'), max_digits=10, decimal_places=2)
    fecha_deteccion = models.DateTimeField(_('fecha de detección'), auto_now_add=True)
    fecha_resolucion = models.DateTimeField(_('fecha de resolución'), null=True, blank=True)
    estado = models.CharField(_('estado'), max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    notas = models.TextField(_('notas'), blank=True)
    notificado = models.BooleanField(_('notificado'), default=False)
    
    class Meta:
        verbose_name = _('alerta de stock')
        verbose_name_plural = _('alertas de stock')
        ordering = ['-fecha_deteccion']
    
    def __str__(self):
        return f"Alerta de stock para {self.producto.nombre} ({self.stock_actual}/{self.stock_minimo})"