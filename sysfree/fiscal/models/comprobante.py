from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import ModeloBase
from inventario.models import Proveedor


class Comprobante(ModeloBase):
    """Modelo para comprobantes fiscales (facturas, retenciones, etc.)."""
    
    TIPO_CHOICES = (
        ('factura', _('Factura')),
        ('nota_credito', _('Nota de Crédito')),
        ('nota_debito', _('Nota de Débito')),
        ('retencion', _('Retención')),
        ('liquidacion', _('Liquidación de Compra')),
    )
    
    ESTADO_CHOICES = (
        ('borrador', _('Borrador')),
        ('emitido', _('Emitido')),
        ('anulado', _('Anulado')),
    )
    
    numero = models.CharField(_('número'), max_length=20, unique=True)
    tipo = models.CharField(_('tipo'), max_length=15, choices=TIPO_CHOICES)
    fecha_emision = models.DateField(_('fecha de emisión'))
    proveedor = models.ForeignKey(
        Proveedor,
        verbose_name=_('proveedor'),
        on_delete=models.PROTECT,
        related_name='comprobantes'
    )
    subtotal = models.DecimalField(_('subtotal'), max_digits=12, decimal_places=2, default=0)
    impuestos = models.DecimalField(_('impuestos'), max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(_('total'), max_digits=12, decimal_places=2, default=0)
    estado = models.CharField(_('estado'), max_length=10, choices=ESTADO_CHOICES, default='borrador')
    
    # Campos para documentos relacionados
    comprobante_relacionado = models.ForeignKey(
        'self',
        verbose_name=_('comprobante relacionado'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='comprobantes_relacionados'
    )
    
    # Campos para asiento contable
    asiento_contable = models.ForeignKey(
        'AsientoContable',
        verbose_name=_('asiento contable'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='comprobantes'
    )
    
    class Meta:
        verbose_name = _('comprobante')
        verbose_name_plural = _('comprobantes')
        ordering = ['-fecha_emision', '-numero']
    
    def __str__(self):
        return f"{self.get_tipo_display()} {self.numero} - {self.proveedor}"