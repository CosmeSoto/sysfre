from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from core.models import ModeloBase
from inventario.models import Producto
from .pedido import Pedido
from core.services import IVAService


class DetallePedido(ModeloBase):
    """Modelo para detalles de pedidos en la tienda online."""
    
    pedido = models.ForeignKey(
        Pedido,
        verbose_name=_('pedido'),
        on_delete=models.CASCADE,
        related_name='detalles'
    )
    
    # Campos para el tipo de item (producto o servicio)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to={
            'model__in': ('producto', 'servicioreparacion')
        }
    )
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    
    # Campo para compatibilidad con código existente
    producto = models.ForeignKey(
        Producto,
        verbose_name=_('producto'),
        on_delete=models.PROTECT,
        related_name='detalles_pedido',
        null=True,
        blank=True
    )
    
    es_servicio = models.BooleanField(_('es servicio'), default=False)
    cantidad = models.PositiveIntegerField(_('cantidad'), default=1)
    precio_unitario = models.DecimalField(_('precio unitario'), max_digits=10, decimal_places=2)
    impuesto_unitario = models.DecimalField(_('impuesto unitario'), max_digits=10, decimal_places=2, default=0)
    subtotal = models.DecimalField(_('subtotal'), max_digits=10, decimal_places=2)
    impuestos = models.DecimalField(_('impuestos'), max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(_('total'), max_digits=10, decimal_places=2)
    
    # Campo para reparación generada (si es un servicio)
    reparacion = models.ForeignKey(
        'reparaciones.Reparacion',
        verbose_name=_('reparación generada'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='detalles_pedido'
    )
    
    class Meta:
        verbose_name = _('detalle de pedido')
        verbose_name_plural = _('detalles de pedido')
        ordering = ['id']
    
    def __str__(self):
        item_name = self.producto.nombre if self.producto else self.item.__str__()
        return f"{item_name} x {self.cantidad} en {self.pedido}"
    
    def save(self, *args, **kwargs):
        """Sobrescribe el método save para calcular los totales y el impuesto unitario."""
        # Calcular tipo_iva
        tipo_iva = None
        if self.es_servicio and hasattr(self.item, 'tipo_iva'):
            tipo_iva = self.item.tipo_iva
        elif self.producto and hasattr(self.producto, 'tipo_iva'):
            tipo_iva = self.producto.tipo_iva

        tipo_iva = tipo_iva or IVAService.get_default()
        monto_iva, _ = IVAService.calcular_iva(self.precio_unitario, tipo_iva)
        self.impuesto_unitario = monto_iva

        self.subtotal = self.precio_unitario * self.cantidad
        self.impuestos = self.impuesto_unitario * self.cantidad
        self.total = self.subtotal + self.impuestos
        super().save(*args, **kwargs)