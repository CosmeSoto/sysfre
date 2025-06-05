from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import ModeloBase
from clientes.models import Cliente, DireccionCliente
from inventario.models import Producto


class Proforma(ModeloBase):
    """Modelo para proformas."""
    
    ESTADO_CHOICES = (
        ('borrador', _('Borrador')),
        ('enviada', _('Enviada')),
        ('aceptada', _('Aceptada')),
        ('rechazada', _('Rechazada')),
        ('vencida', _('Vencida')),
        ('facturada', _('Facturada')),
    )
    
    numero = models.CharField(_('número'), max_length=20, unique=True)
    fecha = models.DateTimeField(_('fecha'), auto_now_add=True)
    cliente = models.ForeignKey(
        Cliente,
        verbose_name=_('cliente'),
        on_delete=models.PROTECT,
        related_name='proformas'
    )
    direccion_facturacion = models.ForeignKey(
        DireccionCliente,
        verbose_name=_('dirección de facturación'),
        on_delete=models.PROTECT,
        related_name='proformas_facturacion',
        null=True,
        blank=True
    )
    direccion_envio = models.ForeignKey(
        DireccionCliente,
        verbose_name=_('dirección de envío'),
        on_delete=models.PROTECT,
        related_name='proformas_envio',
        null=True,
        blank=True
    )
    estado = models.CharField(_('estado'), max_length=10, choices=ESTADO_CHOICES, default='borrador')
    subtotal = models.DecimalField(_('subtotal'), max_digits=10, decimal_places=2, default=0)
    iva = models.DecimalField(_('IVA'), max_digits=10, decimal_places=2, default=0)
    descuento = models.DecimalField(_('descuento'), max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(_('total'), max_digits=10, decimal_places=2, default=0)
    validez = models.PositiveIntegerField(_('validez (días)'), default=15)
    notas = models.TextField(_('notas'), blank=True)
    reparacion = models.ForeignKey(
        'reparaciones.Reparacion',
        verbose_name=_('reparación'),
        on_delete=models.SET_NULL,
        related_name='proformas',
        null=True,
        blank=True
    )
    factura = models.ForeignKey(
        'Venta',
        verbose_name=_('factura'),
        on_delete=models.SET_NULL,
        related_name='proformas',
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = _('proforma')
        verbose_name_plural = _('proformas')
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.numero} - {self.cliente}"


class DetalleProforma(ModeloBase):
    """Modelo para detalles de proformas."""
    
    proforma = models.ForeignKey(
        Proforma,
        verbose_name=_('proforma'),
        on_delete=models.CASCADE,
        related_name='detalles'
    )
    producto = models.ForeignKey(
        Producto,
        verbose_name=_('producto'),
        on_delete=models.PROTECT,
        related_name='detalles_proforma'
    )
    cantidad = models.DecimalField(_('cantidad'), max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(_('precio unitario'), max_digits=10, decimal_places=2)
    descuento = models.DecimalField(_('descuento'), max_digits=10, decimal_places=2, default=0)
    iva = models.DecimalField(_('IVA'), max_digits=10, decimal_places=2, default=0)
    subtotal = models.DecimalField(_('subtotal'), max_digits=10, decimal_places=2)
    total = models.DecimalField(_('total'), max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = _('detalle de proforma')
        verbose_name_plural = _('detalles de proforma')
    
    def __str__(self):
        return f"{self.producto} x {self.cantidad}"