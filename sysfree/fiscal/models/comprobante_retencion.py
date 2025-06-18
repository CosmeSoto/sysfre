from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from core.models import ModeloBase
from ventas.models import Venta
from .retencion import Retencion


class ComprobanteRetencion(ModeloBase):
    """Modelo para comprobantes de retención."""
    
    numero = models.CharField(_('número'), max_length=20, unique=True)
    venta = models.ForeignKey(
        Venta,
        verbose_name=_('venta'),
        on_delete=models.PROTECT,
        related_name='comprobantes_retencion'
    )
    fecha_emision = models.DateField(_('fecha de emisión'))
    base_imponible = models.DecimalField(_('base imponible'), max_digits=10, decimal_places=2)
    total_retenido = models.DecimalField(_('total retenido'), max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = _('comprobante de retención')
        verbose_name_plural = _('comprobantes de retención')
        ordering = ['-fecha_emision']
    
    def __str__(self):
        return f"{self.numero} - {self.venta.numero}"
    
    def clean(self):
        """Valida que los montos sean positivos."""
        if self.base_imponible < 0:
            raise ValidationError(_('La base imponible no puede ser negativa.'))
        if self.total_retenido < 0:
            raise ValidationError(_('El total retenido no puede ser negativo.'))
        super().clean()


class DetalleRetencion(ModeloBase):
    """Modelo para detalles de retención."""
    
    comprobante = models.ForeignKey(
        ComprobanteRetencion,
        verbose_name=_('comprobante'),
        on_delete=models.CASCADE,
        related_name='detalles'
    )
    retencion = models.ForeignKey(
        Retencion,
        verbose_name=_('retención'),
        on_delete=models.PROTECT,
        related_name='detalles'
    )
    base_imponible = models.DecimalField(_('base imponible'), max_digits=10, decimal_places=2)
    valor = models.DecimalField(_('valor'), max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = _('detalle de retención')
        verbose_name_plural = _('detalles de retención')
        ordering = ['id']
    
    def __str__(self):
        return f"{self.retencion} - {self.comprobante}"
    
    def clean(self):
        """Valida que los montos sean positivos."""
        if self.base_imponible < 0:
            raise ValidationError(_('La base imponible no puede ser negativa.'))
        if self.valor < 0:
            raise ValidationError(_('El valor no puede ser negativo.'))
        super().clean()