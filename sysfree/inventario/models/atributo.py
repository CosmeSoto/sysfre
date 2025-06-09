from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import ModeloBase


class Atributo(ModeloBase):
    """Modelo para atributos de productos (ej. Color, Talla, Material)."""
    
    nombre = models.CharField(_('nombre'), max_length=100, unique=True)
    descripcion = models.TextField(_('descripción'), blank=True)
    categorias = models.ManyToManyField(
        'Categoria',
        verbose_name=_('categorías'),
        related_name='atributos',
        blank=True,
        help_text=_('Categorías a las que aplica este atributo')
    )
    activo = models.BooleanField(_('activo'), default=True, help_text=_('Indica si el atributo está activo'))
    
    class Meta:
        verbose_name = _('atributo')
        verbose_name_plural = _('atributos')
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['nombre']),
        ]
    
    def __str__(self):
        return self.nombre