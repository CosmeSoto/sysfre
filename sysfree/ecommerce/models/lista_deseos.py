from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from core.models import ModeloBase
from clientes.models import Cliente


class ListaDeseos(ModeloBase):
    """Modelo para listas de deseos de clientes."""
    
    cliente = models.OneToOneField(
        Cliente,
        verbose_name=_('cliente'),
        on_delete=models.CASCADE,
        related_name='lista_deseos'
    )
    nombre = models.CharField(_('nombre'), max_length=100, default=_('Mi lista de deseos'))
    
    class Meta:
        verbose_name = _('lista de deseos')
        verbose_name_plural = _('listas de deseos')
    
    def __str__(self):
        return f"{self.nombre} - {self.cliente}"
    
    @property
    def total_items(self):
        """Retorna el número total de items en la lista de deseos."""
        return self.items.count()


class ItemListaDeseos(ModeloBase):
    """Modelo para items en la lista de deseos."""
    
    lista = models.ForeignKey(
        ListaDeseos,
        verbose_name=_('lista de deseos'),
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
        'inventario.Producto',
        verbose_name=_('producto'),
        on_delete=models.CASCADE,
        related_name='items_lista_deseos',
        null=True,
        blank=True
    )
    
    es_servicio = models.BooleanField(_('es servicio'), default=False)
    fecha_agregado = models.DateTimeField(_('fecha agregado'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('item de lista de deseos')
        verbose_name_plural = _('items de lista de deseos')
        ordering = ['-fecha_agregado']
        unique_together = ('lista', 'content_type', 'object_id')
    
    def __str__(self):
        item_name = self.producto.nombre if self.producto else str(self.item)
        return f"{item_name} en {self.lista}"