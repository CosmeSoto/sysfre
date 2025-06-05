from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import ModeloBase


class CategoriaEcommerce(ModeloBase):
    """Modelo para categorías de la tienda online."""
    
    nombre = models.CharField(_('nombre'), max_length=100)
    slug = models.SlugField(_('slug'), max_length=100, unique=True)
    descripcion = models.TextField(_('descripción'), blank=True)
    imagen = models.ImageField(_('imagen'), upload_to='ecommerce/categorias/', blank=True, null=True)
    categoria_padre = models.ForeignKey(
        'self',
        verbose_name=_('categoría padre'),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategorias'
    )
    orden = models.PositiveIntegerField(_('orden'), default=0)
    mostrar_en_menu = models.BooleanField(_('mostrar en menú'), default=True)
    
    class Meta:
        verbose_name = _('categoría de tienda')
        verbose_name_plural = _('categorías de tienda')
        ordering = ['orden', 'nombre']
    
    def __str__(self):
        return self.nombre
    
    def save(self, *args, **kwargs):
        """Sobrescribe el método save para generar el slug si está vacío."""
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)