from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from core.models import ModeloBase
from .producto import Producto
from .proveedor import Proveedor
from .almacen import Almacen
from .lote import Lote
from .stock_almacen import StockAlmacen
from decimal import Decimal
from django.db.models import Sum

class MovimientoInventario(ModeloBase):
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
    almacen = models.ForeignKey(
        Almacen,
        verbose_name=_('almacén'),
        on_delete=models.PROTECT,
        related_name='movimientos'
    )
    lote = models.ForeignKey(
        Lote,
        verbose_name=_('lote'),
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='movimientos'
    )
    documento = models.CharField(_('documento'), max_length=50, blank=True)
    notas = models.TextField(_('notas'), blank=True)
    
    referencia_id = models.PositiveIntegerField(_('ID de referencia'), null=True, blank=True)
    referencia_tipo = models.CharField(_('tipo de referencia'), max_length=50, blank=True)
    
    class Meta:
        verbose_name = _('movimiento de inventario')
        verbose_name_plural = _('movimientos de inventario')
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.producto} - {self.cantidad:.2f}"
    
    def clean(self):
        super().clean()
        if self.cantidad is None:
            raise ValidationError(_('La cantidad no puede ser nula.'))
        if self.cantidad < 0:
            raise ValidationError(_('La cantidad no puede ser negativa.'))
        if not self.almacen:
            raise ValidationError(_('El almacén es obligatorio.'))
        if self.tipo == 'entrada':
            expected_stock = self.stock_anterior + self.cantidad
            if self.costo_unitario is None:
                raise ValidationError(_('El costo unitario es obligatorio para movimientos de entrada.'))
        elif self.tipo == 'salida':
            expected_stock = self.stock_anterior - self.cantidad
            if self.producto.es_inventariable:
                stock_almacen = StockAlmacen.objects.filter(producto=self.producto, almacen=self.almacen).first()
                if not stock_almacen or self.cantidad > stock_almacen.cantidad:
                    raise ValidationError(_('La cantidad solicitada excede el stock disponible en el almacén.'))
        else:
            expected_stock = self.stock_nuevo
        if self.tipo in ['entrada', 'salida'] and self.stock_nuevo != expected_stock:
            raise ValidationError(_('El stock nuevo no coincide con el cálculo esperado.'))
        if self.lote and self.lote.producto != self.producto:
            raise ValidationError(_('El lote debe corresponder al producto seleccionado.'))
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        stock_almacen, _ = StockAlmacen.objects.get_or_create(
            producto=self.producto,
            almacen=self.almacen,
            defaults={'cantidad': Decimal('0.00')}
        )
        stock_almacen.cantidad = self.stock_nuevo
        stock_almacen.save()
        total_stock = StockAlmacen.objects.filter(producto=self.producto).aggregate(
            total=Sum('cantidad')
        )['total'] or Decimal('0.00')
        if self.producto.variaciones.exists():
            total_stock = self.producto.variaciones.aggregate(
                total=Sum('stock')
            )['total'] or Decimal('0.00')
        self.producto.stock = total_stock
        self.producto.save(update_fields=['stock'])