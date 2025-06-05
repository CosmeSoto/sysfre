from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import ModeloBase
from .categoria import Categoria


class Producto(ModeloBase):
    """Modelo para productos del inventario."""
    
    ESTADO_CHOICES = (
        ('activo', _('Activo')),
        ('inactivo', _('Inactivo')),
        ('descontinuado', _('Descontinuado')),
    )
    
    TIPO_CHOICES = (
        ('producto', _('Producto')),
        ('servicio', _('Servicio')),
    )
    
    codigo = models.CharField(_('código'), max_length=50, unique=True)
    nombre = models.CharField(_('nombre'), max_length=200)
    descripcion = models.TextField(_('descripción'), blank=True)
    precio_compra = models.DecimalField(_('precio de compra'), max_digits=10, decimal_places=2, default=0)
    precio_venta = models.DecimalField(_('precio de venta'), max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(_('stock'), default=0)
    stock_minimo = models.PositiveIntegerField(_('stock mínimo'), default=0)
    categoria = models.ForeignKey(
        Categoria,
        verbose_name=_('categoría'),
        on_delete=models.PROTECT,
        related_name='productos'
    )
    imagen = models.ImageField(_('imagen'), upload_to='productos/', blank=True, null=True)
    estado = models.CharField(_('estado'), max_length=15, choices=ESTADO_CHOICES, default='activo')
    tipo = models.CharField(_('tipo'), max_length=10, choices=TIPO_CHOICES, default='producto')
    iva = models.DecimalField(_('IVA (%)'), max_digits=5, decimal_places=2, default=12.00)
    es_inventariable = models.BooleanField(_('es inventariable'), default=True)
    
    # Campos para comercio electrónico
    mostrar_en_tienda = models.BooleanField(_('mostrar en tienda'), default=True)
    destacado = models.BooleanField(_('destacado'), default=False)
    url_slug = models.SlugField(_('URL slug'), max_length=255, blank=True)
    
    # Campos para control de inventario
    fecha_ultima_compra = models.DateField(_('fecha última compra'), null=True, blank=True)
    fecha_ultimo_movimiento = models.DateTimeField(_('fecha último movimiento'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('producto')
        verbose_name_plural = _('productos')
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    @property
    def disponible(self):
        """Indica si el producto está disponible para la venta."""
        return self.estado == 'activo' and (not self.es_inventariable or self.stock > 0)
    
    @property
    def margen(self):
        """Calcula el margen de ganancia del producto."""
        if self.precio_compra and self.precio_compra > 0:
            return ((self.precio_venta - self.precio_compra) / self.precio_compra) * 100
        return 0
    
    def save(self, *args, **kwargs):
        """Sobrescribe el método save para generar el slug si está vacío."""
        if not self.url_slug and self.nombre:
            from django.utils.text import slugify
            self.url_slug = slugify(self.nombre)
        super().save(*args, **kwargs)