from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from core.models import ModeloBase, TipoIVA
from core.services import IVAService
from .categoria import Categoria
from .proveedor import Proveedor
from decimal import Decimal

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
    stock = models.DecimalField(_('stock'), max_digits=10, decimal_places=2, default=0)
    stock_minimo = models.DecimalField(_('stock mínimo'), max_digits=10, decimal_places=2, default=0)
    proveedores = models.ManyToManyField(
        Proveedor,
        verbose_name=_('proveedores'),
        related_name='productos',
        blank=True
    )
    categoria = models.ForeignKey(
        Categoria,
        verbose_name=_('categoría'),
        on_delete=models.PROTECT,
        related_name='productos'
    )
    imagen = models.ImageField(_('imagen'), upload_to='productos/', blank=True, null=True)
    estado = models.CharField(_('estado'), max_length=15, choices=ESTADO_CHOICES, default='activo')
    tipo = models.CharField(_('tipo'), max_length=10, choices=TIPO_CHOICES, default='producto')
    tipo_iva = models.ForeignKey(
        TipoIVA,
        verbose_name=_('tipo de IVA'),
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='productos'
    )
    es_inventariable = models.BooleanField(_('es inventariable'), default=True)
    
    mostrar_en_tienda = models.BooleanField(_('mostrar en tienda'), default=True)
    destacado = models.BooleanField(_('destacado'), default=False)
    url_slug = models.SlugField(_('URL slug'), max_length=255, blank=True)
    
    fecha_ultima_compra = models.DateField(_('fecha última compra'), null=True, blank=True)
    fecha_ultimo_movimiento = models.DateTimeField(_('fecha último movimiento'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('producto')
        verbose_name_plural = _('productos')
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['codigo', 'url_slug'])
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    @property
    def disponible(self):
        return self.estado == 'activo' and (not self.es_inventariable or self.stock > 0)
    
    @property
    def margen(self):
        if self.precio_compra and self.precio_compra > 0:
            return ((self.precio_venta - self.precio_compra) / self.precio_compra) * 100
        return 0
    
    def clean(self):
        if self.precio_compra is not None and self.precio_compra < 0:
            raise ValidationError(_('El precio de compra no puede ser negativo.'))
        if self.precio_venta is not None and self.precio_venta < 0:
            raise ValidationError(_('El precio de venta no puede ser negativo.'))
        if self.iva is not None and self.iva < 0:
            raise ValidationError(_('El IVA no puede ser negativo.'))
        if self.stock is not None and self.stock < 0:
            raise ValidationError(_('El stock no puede ser negativo.'))
        if self.stock_minimo is not None and self.stock_minimo < 0:
            raise ValidationError(_('El stock mínimo no puede ser negativo.'))
        super().clean()
    
    def save(self, *args, **kwargs):
        if not self.url_slug and self.nombre:
            from django.utils.text import slugify
            self.url_slug = slugify(self.nombre)
            
        # Si no tiene tipo_iva asignado, usar el predeterminado
        if not self.tipo_iva:
            self.tipo_iva = IVAService.get_default()
            
        # Sincronizar el campo iva con el porcentaje del tipo_iva
        if self.tipo_iva:
            self.iva = self.tipo_iva.porcentaje
            
        super().save(*args, **kwargs)