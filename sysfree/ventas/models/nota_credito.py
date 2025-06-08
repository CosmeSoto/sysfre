from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from core.models import ModeloBase
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
    iva = models.DecimalField(_('IVA'), max_digits=10, decimal_places=2, default=0)
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
        if self.iva < 0:
            raise ValidationError(_('El IVA no puede ser negativo.'))
        if self.total < 0:
            raise ValidationError(_('El total no puede ser negativo.'))
    
    def save(self, *args, **kwargs):
        """Sincroniza subtotal, IVA y total con los detalles."""
        # Guardar primero para obtener un pk
        super().save(*args, **kwargs)
        # Solo sincronizar si la instancia ya tiene un pk y hay detalles
        if self.pk and self.detalles.exists():
            self.subtotal = sum(detalle.subtotal for detalle in self.detalles.all())
            self.iva = sum(detalle.iva for detalle in self.detalles.all())
            self.total = sum(detalle.total for detalle in self.detalles.all())
            # Guardar nuevamente para actualizar los valores calculados
            super().save(*args, **kwargs)


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
    iva = models.DecimalField(_('IVA'), max_digits=10, decimal_places=2, default=0)
    subtotal = models.DecimalField(_('subtotal'), max_digits=10, decimal_places=2)
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
        if self.iva < 0:
            raise ValidationError(_('El IVA no puede ser negativo.'))
    
    def save(self, *args, **kwargs):
        """Calcula subtotal y total, y actualiza el stock."""
        self.subtotal = self.cantidad * self.precio_unitario
        self.total = self.subtotal + self.iva
        super().save(*args, **kwargs)
        if self.nota_credito.estado == 'emitida' and self.producto.es_inventariable:
            self.producto.stock += self.cantidad
            self.producto.save()