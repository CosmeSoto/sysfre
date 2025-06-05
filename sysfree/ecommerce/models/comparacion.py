from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import ModeloBase
from clientes.models import Cliente
from inventario.models import Producto


class Comparacion(ModeloBase):
    """Modelo para comparaciones de productos."""
    
    cliente = models.ForeignKey(
        Cliente,
        verbose_name=_('cliente'),
        on_delete=models.CASCADE,
        related_name='comparaciones',
        null=True,
        blank=True
    )
    sesion_id = models.CharField(_('ID de sesión'), max_length=100, blank=True)
    productos = models.ManyToManyField(
        Producto,
        verbose_name=_('productos'),
        related_name='comparaciones'
    )
    fecha_creacion = models.DateTimeField(_('fecha de creación'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('comparación')
        verbose_name_plural = _('comparaciones')
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        if self.cliente:
            return f"Comparación de {self.cliente}"
        return f"Comparación {self.id}"
    
    @property
    def total_productos(self):
        """Retorna el número total de productos en la comparación."""
        return self.productos.count()