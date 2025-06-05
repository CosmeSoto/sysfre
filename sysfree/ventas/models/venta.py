from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from core.models import ModeloBase
from clientes.models import Cliente, DireccionCliente
from inventario.models import Producto


class Venta(ModeloBase):
    """Modelo para ventas."""
    
    TIPO_CHOICES = (
        ('factura', _('Factura')),
        ('proforma', _('Proforma')),
        ('nota_venta', _('Nota de Venta')),
        ('ticket', _('Ticket')),
    )
    
    ESTADO_CHOICES = (
        ('borrador', _('Borrador')),
        ('emitida', _('Emitida')),
        ('pagada', _('Pagada')),
        ('anulada', _('Anulada')),
    )
    
    numero = models.CharField(_('número'), max_length=20, unique=True)
    fecha = models.DateTimeField(_('fecha'), auto_now_add=True)
    cliente = models.ForeignKey(
        Cliente,
        verbose_name=_('cliente'),
        on_delete=models.PROTECT,
        related_name='ventas'
    )
    direccion_facturacion = models.ForeignKey(
        DireccionCliente,
        verbose_name=_('dirección de facturación'),
        on_delete=models.PROTECT,
        related_name='ventas_facturacion',
        null=True,
        blank=True
    )
    direccion_envio = models.ForeignKey(
        DireccionCliente,
        verbose_name=_('dirección de envío'),
        on_delete=models.PROTECT,
        related_name='ventas_envio',
        null=True,
        blank=True
    )
    tipo = models.CharField(_('tipo'), max_length=10, choices=TIPO_CHOICES, default='factura')
    estado = models.CharField(_('estado'), max_length=10, choices=ESTADO_CHOICES, default='borrador')
    subtotal = models.DecimalField(_('subtotal'), max_digits=10, decimal_places=2, default=0)
    iva = models.DecimalField(_('IVA'), max_digits=10, decimal_places=2, default=0)
    descuento = models.DecimalField(_('descuento'), max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(_('total'), max_digits=10, decimal_places=2, default=0)
    validez = models.PositiveIntegerField(_('validez (días)'), default=15, help_text=_('Solo para proformas'))
    
    # Campos para facturación electrónica
    clave_acceso = models.CharField(_('clave de acceso'), max_length=49, blank=True)
    numero_autorizacion = models.CharField(_('número de autorización'), max_length=49, blank=True)
    fecha_autorizacion = models.DateTimeField(_('fecha de autorización'), null=True, blank=True)
    
    # Campos para seguimiento
    fecha_pago = models.DateTimeField(_('fecha de pago'), null=True, blank=True)
    fecha_envio = models.DateTimeField(_('fecha de envío'), null=True, blank=True)
    fecha_entrega = models.DateTimeField(_('fecha de entrega'), null=True, blank=True)
    
    # Referencias
    reparacion = models.ForeignKey(
        'reparaciones.Reparacion',
        verbose_name=_('reparación'),
        on_delete=models.SET_NULL,
        related_name='ventas',
        null=True,
        blank=True
    )
    venta_relacionada = models.ForeignKey(
        'self',
        verbose_name=_('venta relacionada'),
        on_delete=models.SET_NULL,
        related_name='ventas_relacionadas',
        null=True,
        blank=True,
        help_text=_('Para proformas convertidas a facturas o viceversa')
    )
    
    notas = models.TextField(_('notas'), blank=True)
    
    class Meta:
        verbose_name = _('venta')
        verbose_name_plural = _('ventas')
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.numero} - {self.cliente}"
    
    @property
    def esta_pagado(self):
        """Indica si la venta está completamente pagada."""
        if self.estado == 'pagada':
            return True
        
        total_pagado = sum(pago.monto for pago in self.pagos.filter(estado='aprobado'))
        return total_pagado >= self.total
    
    @property
    def esta_vencida(self):
        """Indica si la proforma está vencida."""
        if self.tipo != 'proforma':
            return False
        
        fecha_vencimiento = self.fecha + timezone.timedelta(days=self.validez)
        return timezone.now() > fecha_vencimiento


class DetalleVenta(ModeloBase):
    """Modelo para detalles de ventas."""
    
    venta = models.ForeignKey(
        Venta,
        verbose_name=_('venta'),
        on_delete=models.CASCADE,
        related_name='detalles'
    )
    producto = models.ForeignKey(
        Producto,
        verbose_name=_('producto'),
        on_delete=models.PROTECT,
        related_name='detalles_venta'
    )
    cantidad = models.DecimalField(_('cantidad'), max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(_('precio unitario'), max_digits=10, decimal_places=2)
    descuento = models.DecimalField(_('descuento'), max_digits=10, decimal_places=2, default=0)
    iva = models.DecimalField(_('IVA'), max_digits=10, decimal_places=2, default=0)
    subtotal = models.DecimalField(_('subtotal'), max_digits=10, decimal_places=2)
    total = models.DecimalField(_('total'), max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = _('detalle de venta')
        verbose_name_plural = _('detalles de venta')
    
    def __str__(self):
        return f"{self.producto} x {self.cantidad}"