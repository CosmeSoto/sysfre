from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import ModeloBase


class Categoria(ModeloBase):
    """Modelo para categorías de productos."""
    
    nombre = models.CharField(_('nombre'), max_length=100)
    descripcion = models.TextField(_('descripción'), blank=True)
    imagen = models.ImageField(_('imagen'), upload_to='categorias/', null=True, blank=True)
    
    class Meta:
        verbose_name = _('categoría')
        verbose_name_plural = _('categorías')
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Producto(ModeloBase):
    """Modelo para productos."""
    
    ESTADO_CHOICES = (
        ('activo', _('Activo')),
        ('inactivo', _('Inactivo')),
        ('descontinuado', _('Descontinuado')),
    )
    
    codigo = models.CharField(_('código'), max_length=50, unique=True)
    nombre = models.CharField(_('nombre'), max_length=200)
    descripcion = models.TextField(_('descripción'), blank=True)
    precio_compra = models.DecimalField(_('precio de compra'), max_digits=10, decimal_places=2)
    precio_venta = models.DecimalField(_('precio de venta'), max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(_('stock'), default=0)
    stock_minimo = models.PositiveIntegerField(_('stock mínimo'), default=5)
    categoria = models.ForeignKey(
        Categoria,
        verbose_name=_('categoría'),
        on_delete=models.PROTECT,
        related_name='productos'
    )
    imagen = models.ImageField(_('imagen'), upload_to='productos/', null=True, blank=True)
    estado = models.CharField(_('estado'), max_length=15, choices=ESTADO_CHOICES, default='activo')
    mostrar_en_tienda = models.BooleanField(_('mostrar en tienda'), default=True)
    es_inventariable = models.BooleanField(_('es inventariable'), default=True)
    
    class Meta:
        verbose_name = _('producto')
        verbose_name_plural = _('productos')
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Proveedor(ModeloBase):
    """Modelo para proveedores."""
    
    nombre = models.CharField(_('nombre'), max_length=200)
    ruc = models.CharField(_('RUC'), max_length=13, unique=True)
    direccion = models.TextField(_('dirección'), blank=True)
    telefono = models.CharField(_('teléfono'), max_length=15, blank=True)
    email = models.EmailField(_('correo electrónico'), blank=True)
    sitio_web = models.URLField(_('sitio web'), blank=True)
    contacto = models.CharField(_('persona de contacto'), max_length=200, blank=True)
    notas = models.TextField(_('notas'), blank=True)
    
    class Meta:
        verbose_name = _('proveedor')
        verbose_name_plural = _('proveedores')
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre