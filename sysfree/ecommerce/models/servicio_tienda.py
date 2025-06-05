from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import ModeloBase
from reparaciones.models import ServicioReparacion
from .categoria_tienda import CategoriaEcommerce


class ServicioEcommerce(ModeloBase):
    """Modelo para servicios de reparación en la tienda online."""
    
    servicio = models.OneToOneField(
        ServicioReparacion,
        verbose_name=_('servicio'),
        on_delete=models.CASCADE,
        related_name='ecommerce'
    )
    slug = models.SlugField(_('slug'), max_length=100, unique=True)
    categorias = models.ManyToManyField(
        CategoriaEcommerce,
        verbose_name=_('categorías'),
        related_name='servicios'
    )
    descripcion_corta = models.TextField(_('descripción corta'), blank=True)
    descripcion_larga = models.TextField(_('descripción larga'), blank=True)
    meta_titulo = models.CharField(_('meta título'), max_length=100, blank=True)
    meta_descripcion = models.TextField(_('meta descripción'), blank=True)
    meta_keywords = models.CharField(_('meta keywords'), max_length=200, blank=True)
    destacado = models.BooleanField(_('destacado'), default=False)
    nuevo = models.BooleanField(_('nuevo'), default=False)
    oferta = models.BooleanField(_('oferta'), default=False)
    precio_oferta = models.DecimalField(_('precio de oferta'), max_digits=10, decimal_places=2, null=True, blank=True)
    fecha_inicio_oferta = models.DateTimeField(_('fecha inicio oferta'), null=True, blank=True)
    fecha_fin_oferta = models.DateTimeField(_('fecha fin oferta'), null=True, blank=True)
    orden = models.PositiveIntegerField(_('orden'), default=0)
    visitas = models.PositiveIntegerField(_('visitas'), default=0)
    
    class Meta:
        verbose_name = _('servicio de tienda')
        verbose_name_plural = _('servicios de tienda')
        ordering = ['orden', 'servicio__nombre']
    
    def __str__(self):
        return self.servicio.nombre
    
    def save(self, *args, **kwargs):
        """Sobrescribe el método save para generar el slug si está vacío."""
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.servicio.nombre)
        super().save(*args, **kwargs)
    
    @property
    def precio_actual(self):
        """Retorna el precio actual del servicio (oferta o normal)."""
        from django.utils import timezone
        now = timezone.now()
        
        if self.oferta and self.precio_oferta and self.fecha_inicio_oferta and self.fecha_fin_oferta:
            if self.fecha_inicio_oferta <= now <= self.fecha_fin_oferta:
                return self.precio_oferta
        
        return self.servicio.precio