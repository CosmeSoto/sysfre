from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import ModeloBase
from clientes.models import Cliente


class Carrito(ModeloBase):
    """Modelo para carritos de compra en la tienda online."""
    
    cliente = models.ForeignKey(
        Cliente,
        verbose_name=_('cliente'),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='carritos'
    )
    sesion_id = models.CharField(_('ID de sesión'), max_length=100, blank=True)
    fecha_creacion = models.DateTimeField(_('fecha de creación'), auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(_('fecha de actualización'), auto_now=True)
    convertido_a_pedido = models.BooleanField(_('convertido a pedido'), default=False)
    
    # Campos para almacenar los totales calculados
    _subtotal = models.DecimalField(_('subtotal'), max_digits=10, decimal_places=2, default=0, db_column='subtotal')
    _total_impuestos = models.DecimalField(_('total impuestos'), max_digits=10, decimal_places=2, default=0, db_column='total_impuestos')
    _total = models.DecimalField(_('total'), max_digits=10, decimal_places=2, default=0, db_column='total')
    
    class Meta:
        verbose_name = _('carrito')
        verbose_name_plural = _('carritos')
        ordering = ['-fecha_actualizacion']
    
    def __str__(self):
        if self.cliente:
            return f"Carrito de {self.cliente}"
        return f"Carrito {self.sesion_id}"
    
    @property
    def total_items(self):
        """Retorna el número total de items en el carrito."""
        return sum(item.cantidad for item in self.items.all())
    
    @property
    def subtotal(self):
        """Retorna el subtotal del carrito."""
        return self._subtotal
    
    @subtotal.setter
    def subtotal(self, value):
        """Establece el subtotal del carrito."""
        self._subtotal = value
    
    @property
    def total_impuestos(self):
        """Retorna el total de impuestos del carrito."""
        return self._total_impuestos
    
    @total_impuestos.setter
    def total_impuestos(self, value):
        """Establece el total de impuestos del carrito."""
        self._total_impuestos = value
    
    @property
    def total(self):
        """Retorna el total del carrito."""
        return self._total
    
    @total.setter
    def total(self, value):
        """Establece el total del carrito."""
        self._total = value
    
    def actualizar_totales(self):
        """Actualiza los totales del carrito basados en sus items."""
        self._subtotal = sum(item.subtotal for item in self.items.all())
        self._total_impuestos = sum(item.impuestos for item in self.items.all())
        self._total = self._subtotal + self._total_impuestos
        self.save(update_fields=['_subtotal', '_total_impuestos', '_total'])