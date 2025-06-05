from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import ModeloBase
from .periodo_fiscal import PeriodoFiscal


class AsientoContable(ModeloBase):
    """Modelo para asientos contables."""
    
    ESTADO_CHOICES = (
        ('borrador', _('Borrador')),
        ('validado', _('Validado')),
        ('anulado', _('Anulado')),
    )
    
    TIPO_CHOICES = (
        ('manual', _('Manual')),
        ('venta', _('Venta')),
        ('compra', _('Compra')),
        ('ajuste', _('Ajuste')),
        ('cierre', _('Cierre')),
    )
    
    numero = models.CharField(_('número'), max_length=20, unique=True)
    fecha = models.DateField(_('fecha'))
    periodo_fiscal = models.ForeignKey(
        PeriodoFiscal,
        verbose_name=_('periodo fiscal'),
        on_delete=models.PROTECT,
        related_name='asientos'
    )
    tipo = models.CharField(_('tipo'), max_length=10, choices=TIPO_CHOICES, default='manual')
    concepto = models.CharField(_('concepto'), max_length=200)
    estado = models.CharField(_('estado'), max_length=10, choices=ESTADO_CHOICES, default='borrador')
    notas = models.TextField(_('notas'), blank=True)
    
    # Campos para trazabilidad
    referencia_id = models.PositiveIntegerField(_('ID de referencia'), null=True, blank=True)
    referencia_tipo = models.CharField(_('tipo de referencia'), max_length=50, blank=True)
    
    class Meta:
        verbose_name = _('asiento contable')
        verbose_name_plural = _('asientos contables')
        ordering = ['-fecha', '-numero']
    
    def __str__(self):
        return f"{self.numero} - {self.concepto}"
    
    @property
    def total_debe(self):
        """Retorna el total del debe del asiento."""
        return sum(linea.debe for linea in self.lineas.all())
    
    @property
    def total_haber(self):
        """Retorna el total del haber del asiento."""
        return sum(linea.haber for linea in self.lineas.all())
    
    @property
    def esta_balanceado(self):
        """Indica si el asiento está balanceado (debe = haber)."""
        return self.total_debe == self.total_haber