from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from core.models import ModeloBase
from .producto import Producto
from .almacen import Almacen
from .stock_almacen import StockAlmacen

class Lote(ModeloBase):
    producto = models.ForeignKey(
        Producto,
        verbose_name=_('producto'),
        on_delete=models.PROTECT,
        related_name='lotes'
    )
    numero_lote = models.CharField(_('número de lote'), max_length=50)
    fecha_vencimiento = models.DateField(_('fecha de vencimiento'), null=True, blank=True)
    fecha_produccion = models.DateField(_('fecha de producción'), null=True, blank=True)
    cantidad = models.DecimalField(_('cantidad'), max_digits=10, decimal_places=2)
    almacen = models.ForeignKey(
        Almacen,
        verbose_name=_('almacén'),
        on_delete=models.PROTECT,
        related_name='lotes'
    )
    
    class Meta:
        verbose_name = _('lote')
        verbose_name_plural = _('lotes')
        ordering = ['producto', 'numero_lote']
    
    def __str__(self):
        return f"{self.producto} - Lote {self.numero_lote}"
    
    def clean(self):
        if self.cantidad is None:
            raise ValidationError(_('La cantidad no puede ser nula.'))
        if self.cantidad < 0:
            raise ValidationError(_('La cantidad no puede ser negativa.'))
        if self.fecha_vencimiento and self.fecha_produccion and self.fecha_vencimiento < self.fecha_produccion:
            raise ValidationError(_('La fecha de vencimiento no puede ser anterior a la fecha de producción.'))
        super().clean()
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        stock_almacen, _ = StockAlmacen.objects.get_or_create(
            producto=self.producto,
            almacen=self.almacen,
            defaults={'cantidad': self.cantidad}
        )
        stock_almacen.cantidad = self.cantidad
        stock_almacen.save()