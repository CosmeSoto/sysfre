from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from core.models import ModeloBase
from .proveedor import Proveedor
from .producto import Producto

class OrdenCompra(ModeloBase):
    """Modelo para órdenes de compra a proveedores."""
    
    ESTADO_CHOICES = (
        ('pendiente', _('Pendiente')),
        ('completada', _('Completada')),
        ('cancelada', _('Cancelada')),
    )
    
    proveedor = models.ForeignKey(
        Proveedor,
        verbose_name=_('proveedor'),
        on_delete=models.PROTECT,
        related_name='ordenes_compra'
    )
    numero = models.CharField(_('número'), max_length=20, unique=True)
    fecha = models.DateField(_('fecha'))
    estado = models.CharField(_('estado'), max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    total = models.DecimalField(_('total'), max_digits=12, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = _('orden de compra')
        verbose_name_plural = _('órdenes de compra')
        ordering = ['-fecha']
    
    def __str__(self):
        return f"Orden {self.numero} - {self.proveedor}"
    
    def clean(self):
        """Valida que el total no sea negativo."""
        if self.total < 0:
            raise ValidationError(_('El total no puede ser negativo.'))
        super().clean()

class ItemOrdenCompra(ModeloBase):
    """Modelo para ítems de una orden de compra."""
    
    orden_compra = models.ForeignKey(
        OrdenCompra,
        verbose_name=_('orden de compra'),
        on_delete=models.CASCADE,
        related_name='items'
    )
    producto = models.ForeignKey(
        Producto,
        verbose_name=_('producto'),
        on_delete=models.PROTECT
    )
    cantidad = models.DecimalField(_('cantidad'), max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(_('precio unitario'), max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(_('subtotal'), max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = _('item de orden de compra')
        verbose_name_plural = _('items de órdenes de compra')
        ordering = ['id']
    
    def __str__(self):
        return f"{self.producto} - {self.cantidad}"
    
    def clean(self):
        """Valida que la cantidad y el precio unitario no sean negativos."""
        if self.cantidad < 0:
            raise ValidationError(_('La cantidad no puede ser negativa.'))
        if self.precio_unitario < 0:
            raise ValidationError(_('El precio unitario no puede ser negativo.'))
        super().clean()
    
    def save(self, *args, **kwargs):
        """Calcula el subtotal y actualiza el total de la orden."""
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)
        # Actualiza el total de la orden
        self.orden_compra.total = sum(item.subtotal for item in self.orden_compra.items.all())
        self.orden_compra.save()