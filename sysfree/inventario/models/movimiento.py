from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import ModeloBase
from .producto import Producto
from .proveedor import Proveedor


class MovimientoInventario(ModeloBase):
    """Modelo para registrar movimientos de inventario."""
    
    TIPO_CHOICES = (
        ('entrada', _('Entrada')),
        ('salida', _('Salida')),
        ('ajuste', _('Ajuste')),
        ('devolucion', _('Devolución')),
        ('traslado', _('Traslado')),
    )
    
    ORIGEN_CHOICES = (
        ('compra', _('Compra')),
        ('venta', _('Venta')),
        ('ajuste_manual', _('Ajuste Manual')),
        ('devolucion_cliente', _('Devolución de Cliente')),
        ('devolucion_proveedor', _('Devolución a Proveedor')),
        ('traslado', _('Traslado entre Sucursales')),
        ('inicial', _('Inventario Inicial')),
    )
    
    fecha = models.DateTimeField(_('fecha'), auto_now_add=True)
    tipo = models.CharField(_('tipo'), max_length=15, choices=TIPO_CHOICES)
    origen = models.CharField(_('origen'), max_length=20, choices=ORIGEN_CHOICES)
    producto = models.ForeignKey(
        Producto,
        verbose_name=_('producto'),
        on_delete=models.PROTECT,
        related_name='movimientos'
    )
    cantidad = models.DecimalField(_('cantidad'), max_digits=10, decimal_places=2)
    stock_anterior = models.DecimalField(_('stock anterior'), max_digits=10, decimal_places=2)
    stock_nuevo = models.DecimalField(_('stock nuevo'), max_digits=10, decimal_places=2)
    costo_unitario = models.DecimalField(_('costo unitario'), max_digits=10, decimal_places=2, null=True, blank=True)
    proveedor = models.ForeignKey(
        Proveedor,
        verbose_name=_('proveedor'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimientos'
    )
    documento = models.CharField(_('documento'), max_length=50, blank=True)
    notas = models.TextField(_('notas'), blank=True)
    
    # Campos para trazabilidad
    referencia_id = models.PositiveIntegerField(_('ID de referencia'), null=True, blank=True)
    referencia_tipo = models.CharField(_('tipo de referencia'), max_length=50, blank=True)
    
    class Meta:
        verbose_name = _('movimiento de inventario')
        verbose_name_plural = _('movimientos de inventario')
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.producto} - {self.cantidad}"