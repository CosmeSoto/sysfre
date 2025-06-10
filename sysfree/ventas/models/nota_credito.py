from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from core.models import ModeloBase
from core.services import IVAService
from clientes.models import Cliente
from inventario.models import Producto
from .venta import Venta


class NotaCredito(ModeloBase):
    """Modelo para notas de crédito."""
    
    ESTADO_CHOICES = (
        ('borrador', _('Borrador')),
        ('emitida', _('Emitida')),
        ('anulada', _('Anulada')),
    )
    
    numero = models.CharField(_('número'), max_length=20, unique=True)
    fecha = models.DateTimeField(_('fecha'), auto_now_add=True)
    venta = models.ForeignKey(
        Venta,
        verbose_name=_('venta'),
        on_delete=models.PROTECT,
        related_name='notas_credito'
    )
    cliente = models.ForeignKey(
        Cliente,
        verbose_name=_('cliente'),
        on_delete=models.PROTECT,
        related_name='notas_credito'
    )
    motivo = models.TextField(_('motivo'))
    subtotal = models.DecimalField(_('subtotal'), max_digits=10, decimal_places=2, default=0)
    tipo_iva = models.ForeignKey(
        'core.TipoIVA',
        verbose_name=_('tipo de IVA'),
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='notas_credito'
    )
    total = models.DecimalField(_('total'), max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(_('estado'), max_length=10, choices=ESTADO_CHOICES, default='borrador')
    
    class Meta:
        verbose_name = _('nota de crédito')
        verbose_name_plural = _('notas de crédito')
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.numero} - {self.cliente}"
    
    def clean(self):
        """Valida los campos de la nota de crédito."""
        super().clean()
        if self.subtotal < 0:
            raise ValidationError(_('El subtotal no puede ser negativo.'))
        if self.total < 0:
            raise ValidationError(_('El total no puede ser negativo.'))
    
    def save(self, *args, **kwargs):
        """Sincroniza subtotal y total con los detalles."""
        # Guardar primero para obtener un pk
        super().save(*args, **kwargs)
        # Solo sincronizar si la instancia ya tiene un pk y hay detalles
        if self.pk and self.detalles.exists():
            self.subtotal = sum(detalle.subtotal for detalle in self.detalles.all())
            self.total = sum(detalle.total for detalle in self.detalles.all())
            # Guardar nuevamente para actualizar los valores calculados
            super().save(*args, **kwargs)
    
    @property
    def iva(self):
        """Calcula el IVA total de la nota de crédito basado en los detalles."""
        return sum(detalle.iva for detalle in self.detalles.all()) if self.detalles.exists() else 0


class DetalleNotaCredito(ModeloBase):
    """Modelo para detalles de notas de crédito."""
    
    nota_credito = models.ForeignKey(
        NotaCredito,
        verbose_name=_('nota de crédito'),
        on_delete=models.CASCADE,
        related_name='detalles'
    )
    producto = models.ForeignKey(
        Producto,
        verbose_name=_('producto'),
        on_delete=models.PROTECT,
        related_name='detalles_nota_credito'
    )
    cantidad = models.DecimalField(_('cantidad'), max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(_('precio unitario'), max_digits=10, decimal_places=2)
    tipo_iva = models.ForeignKey(
        'core.TipoIVA',
        verbose_name=_('tipo de IVA'),
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='detalles_nota_credito'
    )
    subtotal = models.DecimalField(_('subtotal'), max_digits=10, decimal_places=2)
    iva = models.DecimalField(_('IVA'), max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(_('total'), max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = _('detalle de nota de crédito')
        verbose_name_plural = _('detalles de notas de crédito')
        ordering = ['id']
    
    def __str__(self):
        return f"{self.producto} x {self.cantidad:.2f}"
    
    def clean(self):
        """Valida los campos del detalle."""
        super().clean()
        if self.cantidad <= 0:
            raise ValidationError(_('La cantidad debe ser positiva.'))
        if self.precio_unitario < 0:
            raise ValidationError(_('El precio unitario no puede ser negativo.'))
    
    def save(self, *args, **kwargs):
        """Calcula subtotal, IVA, total y actualiza el stock."""
        # Calcular subtotal
        self.subtotal = self.cantidad * self.precio_unitario
        
        # Obtener tipo_iva del producto, de la nota de crédito, o el predeterminado
        if not self.tipo_iva:
            self.tipo_iva = (
                getattr(self.producto, 'tipo_iva', None) or
                getattr(self.nota_credito, 'tipo_iva', None) or
                IVAService.get_default()
            )
        
        # Calcular IVA y total usando IVAService
        self.iva, self.total = IVAService.calcular_iva(self.subtotal, self.tipo_iva)
        
        # Guardar el detalle
        super().save(*args, **kwargs)
        
        # Actualizar stock si aplica
        if self.nota_credito.estado == 'emitida' and self.producto.es_inventariable:
            self.producto.stock += self.cantidad
            self.producto.save()