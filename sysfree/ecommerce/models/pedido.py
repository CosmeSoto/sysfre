from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import ModeloBase
from clientes.models import Cliente, DireccionCliente
from ventas.models import Venta
from .carrito import Carrito


class Pedido(ModeloBase):
    """Modelo para pedidos en la tienda online."""
    
    ESTADO_CHOICES = (
        ('pendiente', _('Pendiente de pago')),
        ('pagado', _('Pagado')),
        ('preparando', _('Preparando')),
        ('enviado', _('Enviado')),
        ('entregado', _('Entregado')),
        ('cancelado', _('Cancelado')),
    )
    
    numero = models.CharField(_('número'), max_length=20, unique=True)
    cliente = models.ForeignKey(
        Cliente,
        verbose_name=_('cliente'),
        on_delete=models.PROTECT,
        related_name='pedidos'
    )
    carrito = models.OneToOneField(
        Carrito,
        verbose_name=_('carrito'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pedido'
    )
    fecha = models.DateTimeField(_('fecha'), auto_now_add=True)
    estado = models.CharField(_('estado'), max_length=10, choices=ESTADO_CHOICES, default='pendiente')
    direccion_facturacion = models.ForeignKey(
        DireccionCliente,
        verbose_name=_('dirección de facturación'),
        on_delete=models.SET_NULL,
        null=True,
        related_name='pedidos_facturacion'
    )
    direccion_envio = models.ForeignKey(
        DireccionCliente,
        verbose_name=_('dirección de envío'),
        on_delete=models.SET_NULL,
        null=True,
        related_name='pedidos_envio'
    )
    subtotal = models.DecimalField(_('subtotal'), max_digits=10, decimal_places=2, default=0)
    impuestos = models.DecimalField(_('impuestos'), max_digits=10, decimal_places=2, default=0)
    envio = models.DecimalField(_('costo de envío'), max_digits=10, decimal_places=2, default=0)
    descuento = models.DecimalField(_('descuento'), max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(_('total'), max_digits=10, decimal_places=2, default=0)
    notas = models.TextField(_('notas'), blank=True)
    
    # Campos para seguimiento
    fecha_pago = models.DateTimeField(_('fecha de pago'), null=True, blank=True)
    fecha_envio = models.DateTimeField(_('fecha de envío'), null=True, blank=True)
    fecha_entrega = models.DateTimeField(_('fecha de entrega'), null=True, blank=True)
    codigo_seguimiento = models.CharField(_('código de seguimiento'), max_length=100, blank=True)
    
    # Campos para facturación
    factura = models.OneToOneField(
        Venta,
        verbose_name=_('factura'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pedido'
    )
    
    class Meta:
        verbose_name = _('pedido')
        verbose_name_plural = _('pedidos')
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.numero} - {self.cliente}"