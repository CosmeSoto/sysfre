from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import ModeloBase
from clientes.models import Cliente
from inventario.models import Producto


class Pedido(ModeloBase):
    """Modelo para pedidos online."""
    
    ESTADO_CHOICES = (
        ('pendiente', _('Pendiente')),
        ('pagado', _('Pagado')),
        ('enviado', _('Enviado')),
        ('entregado', _('Entregado')),
        ('cancelado', _('Cancelado')),
    )
    
    numero = models.CharField(_('número'), max_length=20, unique=True)
    fecha = models.DateTimeField(_('fecha'), auto_now_add=True)
    cliente = models.ForeignKey(
        Cliente,
        verbose_name=_('cliente'),
        on_delete=models.PROTECT,
        related_name='pedidos'
    )
    estado = models.CharField(_('estado'), max_length=10, choices=ESTADO_CHOICES, default='pendiente')
    subtotal = models.DecimalField(_('subtotal'), max_digits=10, decimal_places=2, default=0)
    impuestos = models.DecimalField(_('impuestos'), max_digits=10, decimal_places=2, default=0)
    descuento = models.DecimalField(_('descuento'), max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(_('total'), max_digits=10, decimal_places=2, default=0)
    notas = models.TextField(_('notas'), blank=True)
    
    class Meta:
        verbose_name = _('pedido')
        verbose_name_plural = _('pedidos')
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.numero} - {self.cliente}"


class DetallePedido(ModeloBase):
    """Modelo para detalles de pedidos."""
    
    pedido = models.ForeignKey(
        Pedido,
        verbose_name=_('pedido'),
        on_delete=models.CASCADE,
        related_name='detalles'
    )
    producto = models.ForeignKey(
        Producto,
        verbose_name=_('producto'),
        on_delete=models.PROTECT,
        related_name='detalles_pedido',
        null=True,
        blank=True
    )
    es_servicio = models.BooleanField(_('es servicio'), default=False)
    item = models.CharField(_('ítem'), max_length=200, blank=True)
    cantidad = models.PositiveIntegerField(_('cantidad'), default=1)
    precio_unitario = models.DecimalField(_('precio unitario'), max_digits=10, decimal_places=2)
    descuento = models.DecimalField(_('descuento'), max_digits=10, decimal_places=2, default=0)
    subtotal = models.DecimalField(_('subtotal'), max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = _('detalle de pedido')
        verbose_name_plural = _('detalles de pedido')
    
    def __str__(self):
        if self.es_servicio:
            return f"{self.item} x {self.cantidad}"
        return f"{self.producto} x {self.cantidad}"