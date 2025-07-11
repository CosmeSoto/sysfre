from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from core.models import ModeloBase


class Categoria(ModeloBase):
    """Modelo para categorías de productos."""
    
    nombre = models.CharField(_('nombre'), max_length=100)
    descripcion = models.TextField(_('descripción'), blank=True)
    codigo = models.CharField(_('código'), max_length=20, blank=True, null=True, unique=True)
    imagen = models.ImageField(_('imagen'), upload_to='categorias/', blank=True, null=True)
    categoria_padre = models.ForeignKey(
        'self',
        verbose_name=_('categoría padre'),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategorias'
    )
    orden = models.PositiveIntegerField(_('orden'), default=0)
    
    class Meta:
        verbose_name = _('categoría')
        verbose_name_plural = _('categorías')
        ordering = ['orden', 'nombre']
        indexes = [
            models.Index(fields=['codigo'])
        ]
    
    def __str__(self):
        return self.nombre

    def clean(self):
        super().clean()
        if self.orden < 0:
            raise ValidationError(_('El orden no puede ser negativo.'))
        if self.categoria_padre:
            parent = self.categoria_padre
            while parent:
                if parent == self:
                    raise ValidationError(_('Una categoría no puede ser su propio padre.'))
                parent = parent.categoria_padre

    @property
    def ruta_completa(self):
        if self.categoria_padre:
            return f"{self.categoria_padre.ruta_completa} > {self.nombre}"
        return self.nombre