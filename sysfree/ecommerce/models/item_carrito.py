from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from core.models import ModeloBase
from inventario.models import Producto
from .carrito import Carrito
from core.services import IVAService


class ItemCarrito(ModeloBase):
    """Modelo para items en el carrito de compra."""
    carrito = models.ForeignKey(
        Carrito,
        verbose_name=_('carrito'),
        on_delete=models.CASCADE,
        related_name='items'
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
        on_delete=models.CASCADE,
        related_name='items_carrito',
        null=True,
        blank=True
    )

    es_servicio = models.BooleanField(_('es servicio'), default=False)
    cantidad = models.PositiveIntegerField(_('cantidad'), default=1)
    precio_unitario = models.DecimalField(_('precio unitario'), max_digits=10, decimal_places=2)
    impuesto_unitario = models.DecimalField(_('impuesto unitario'), max_digits=10, decimal_places=2, default=0)
    _subtotal = models.DecimalField(_('subtotal'), max_digits=10, decimal_places=2, default=0, db_column='subtotal')
    _impuestos = models.DecimalField(_('impuestos'), max_digits=10, decimal_places=2, default=0, db_column='impuestos')
    _total = models.DecimalField(_('total'), max_digits=10, decimal_places=2, default=0, db_column='total')

    class Meta:
        verbose_name = _('item de carrito')
        verbose_name_plural = _('items de carrito')
        ordering = ['id']
        unique_together = ('carrito', 'content_type', 'object_id')

    def __str__(self):
        item_name = self.producto.nombre if self.producto else self.item.__str__()
        return f"{item_name} x {self.cantidad} en {self.carrito}"

    def save(self, *args, **kwargs):
        """Sobrescribe el método save para actualizar el precio si no se especifica."""
        if not self.precio_unitario:
            if self.es_servicio:
                try:
                    self.precio_unitario = self.item.ecommerce.precio_actual
                except:
                    self.precio_unitario = self.item.precio
            else:
                try:
                    self.precio_unitario = self.producto.ecommerce.precio_actual
                except:
                    self.precio_unitario = self.producto.precio_venta

        # Calcular impuesto unitario usando IVAService y el tipo_iva correcto
        tipo_iva = None
        if self.es_servicio and hasattr(self.item, 'tipo_iva'):
            tipo_iva = self.item.tipo_iva
        elif self.producto and hasattr(self.producto, 'tipo_iva'):
            tipo_iva = self.producto.tipo_iva

        tipo_iva = tipo_iva or IVAService.get_default()
        monto_iva, _ = IVAService.calcular_iva(self.precio_unitario, tipo_iva)
        self.impuesto_unitario = monto_iva
        
        # Calcular totales del item
        self.calcular_totales()

        super().save(*args, **kwargs)
        
        # Actualizar totales del carrito
        if self.carrito:
            try:
                self.carrito.actualizar_totales()
            except Exception as e:
                import logging
                logger = logging.getLogger('sysfree')
                logger.error(f"Error al actualizar totales del carrito: {str(e)}")
                
    def delete(self, *args, **kwargs):
        """Sobrescribe el método delete para actualizar los totales del carrito."""
        carrito = self.carrito
        super().delete(*args, **kwargs)
        
        # Actualizar totales del carrito
        if carrito:
            try:
                carrito.actualizar_totales()
            except Exception as e:
                import logging
                logger = logging.getLogger('sysfree')
                logger.error(f"Error al actualizar totales del carrito: {str(e)}")

    @property
    def subtotal(self):
        """Retorna el subtotal del item."""
        return self._subtotal
    
    @subtotal.setter
    def subtotal(self, value):
        """Establece el subtotal del item."""
        self._subtotal = value

    @property
    def impuestos(self):
        """Retorna el total de impuestos del item."""
        return self._impuestos
    
    @impuestos.setter
    def impuestos(self, value):
        """Establece el total de impuestos del item."""
        self._impuestos = value

    @property
    def total(self):
        """Retorna el total del item."""
        return self._total
    
    @total.setter
    def total(self, value):
        """Establece el total del item."""
        self._total = value
        
    def calcular_totales(self):
        """Calcula y actualiza los totales del item."""
        self._subtotal = self.precio_unitario * self.cantidad
        self._impuestos = self.impuesto_unitario * self.cantidad
        self._total = self._subtotal + self._impuestos