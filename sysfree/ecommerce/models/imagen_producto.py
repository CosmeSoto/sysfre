from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import ModeloBase
from .producto_tienda import ProductoEcommerce


class ImagenProducto(ModeloBase):
    """Modelo para imágenes adicionales de productos en la tienda online."""
    
    producto = models.ForeignKey(
        ProductoEcommerce,
        verbose_name=_('producto'),
        on_delete=models.CASCADE,
        related_name='imagenes'
    )
    imagen = models.ImageField(_('imagen'), upload_to='ecommerce/productos/')
    titulo = models.CharField(_('título'), max_length=100, blank=True)
    alt = models.CharField(_('texto alternativo'), max_length=100, blank=True)
    orden = models.PositiveIntegerField(_('orden'), default=0)
    es_principal = models.BooleanField(_('es principal'), default=False)
    
    class Meta:
        verbose_name = _('imagen de producto')
        verbose_name_plural = _('imágenes de producto')
        ordering = ['orden']
    
    def __str__(self):
        return f"{self.producto} - {self.titulo or 'Imagen'} {self.orden}"
    
    def save(self, *args, **kwargs):
        """Sobrescribe el método save para asegurar que solo haya una imagen principal."""
        if self.es_principal:
            # Desmarcar otras imágenes principales del mismo producto
            ImagenProducto.objects.filter(
                producto=self.producto, 
                es_principal=True
            ).exclude(pk=self.pk).update(es_principal=False)
        super().save(*args, **kwargs)