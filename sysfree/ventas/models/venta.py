from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError
from core.models import ModeloBase
from clientes.models import Cliente, DireccionCliente
from inventario.models import Producto
from core.services import IVAService

class Venta(ModeloBase):
    """Modelo para ventas, incluyendo facturas y proformas."""
    
    TIPO_CHOICES = (
        ('factura', _('Factura')),
        ('nota_venta', _('Nota de Venta')),
        ('ticket', _('Ticket')),
        ('proforma', _('Proforma')),
    )
    
    ESTADO_CHOICES = (
        ('borrador', _('Borrador')),
        ('emitida', _('Emitida')),
        ('pagada', _('Pagada')),
        ('anulada', _('Anulada')),
        ('enviada', _('Enviada')),  # Para proformas
        ('aceptada', _('Aceptada')),  # Para proformas
        ('rechazada', _('Rechazada')),  # Para proformas
        ('vencida', _('Vencida')),  # Para proformas
        ('facturada', _('Facturada')),  # Para proformas
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
    tipo_iva = models.ForeignKey(
        'core.TipoIVA',
        verbose_name=_('tipo de IVA'),
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='ventas'
    )
    descuento = models.DecimalField(_('descuento'), max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(_('total'), max_digits=10, decimal_places=2, default=0)
    validez = models.PositiveIntegerField(_('validez (días)'), default=15)
    
    clave_acceso = models.CharField(_('clave de acceso'), max_length=49, blank=True)
    numero_autorizacion = models.CharField(_('número de autorización'), max_length=49, blank=True)
    fecha_autorizacion = models.DateTimeField(_('fecha de autorización'), null=True, blank=True)
    
    fecha_pago = models.DateTimeField(_('fecha de pago'), null=True, blank=True)
    fecha_envio = models.DateTimeField(_('fecha de envío'), null=True, blank=True)
    fecha_entrega = models.DateTimeField(_('fecha de entrega'), null=True, blank=True)
    
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
        blank=True
    )
    
    notas = models.TextField(_('notas'), blank=True)
    
    class Meta:
        verbose_name = _('venta')
        verbose_name_plural = _('ventas')
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['numero', 'clave_acceso'])
        ]
    
    def __str__(self):
        return f"{self.numero} - {self.cliente}"
    
    def clean(self):
        """Valida los campos de la venta."""
        super().clean()
        if self.subtotal < 0:
            raise ValidationError(_('El subtotal no puede ser negativo.'))
        if self.descuento < 0:
            raise ValidationError(_('El descuento no puede ser negativo.'))
        if self.total < 0:
            raise ValidationError(_('El total no puede ser negativo.'))
        if self.validez <= 0:
            raise ValidationError(_('La validez debe ser positiva.'))
        if self.tipo == 'proforma' and self.estado in ['emitida', 'pagada', 'anulada']:
            raise ValidationError(_('Las proformas no pueden estar en estado emitida, pagada o anulada.'))
    
    def save(self, *args, **kwargs):
        """Sincroniza subtotal, descuento y total con los detalles."""
        # Guardar primero para obtener un pk
        super().save(*args, **kwargs)
        # Solo sincronizar si la instancia ya tiene un pk
        if self.pk and self.detalles.exists():
            self.subtotal = sum(detalle.subtotal for detalle in self.detalles.all())
            self.descuento = sum(detalle.descuento for detalle in self.detalles.all())
            self.total = sum(detalle.total for detalle in self.detalles.all())
            super().save(*args, **kwargs)
    
    @property
    def iva(self):
        """Calcula el IVA total de la venta basado en los detalles."""
        return sum(detalle.iva for detalle in self.detalles.all()) if self.detalles.exists() else 0
    
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