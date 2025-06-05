from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import ModeloBase
from inventario.models import Producto
from clientes.models import Cliente


class Valoracion(ModeloBase):
    """Modelo para valoraciones de productos."""
    
    producto = models.ForeignKey(
        Producto,
        verbose_name=_('producto'),
        on_delete=models.CASCADE,
        related_name='valoraciones'
    )
    cliente = models.ForeignKey(
        Cliente,
        verbose_name=_('cliente'),
        on_delete=models.CASCADE,
        related_name='valoraciones'
    )
    puntuacion = models.PositiveSmallIntegerField(
        _('puntuación'),
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    titulo = models.CharField(_('título'), max_length=100)
    comentario = models.TextField(_('comentario'))
    fecha = models.DateTimeField(_('fecha'), auto_now_add=True)
    aprobado = models.BooleanField(_('aprobado'), default=False)
    
    class Meta:
        verbose_name = _('valoración')
        verbose_name_plural = _('valoraciones')
        ordering = ['-fecha']
        unique_together = ('producto', 'cliente')
    
    def __str__(self):
        return f"{self.cliente} - {self.producto} - {self.puntuacion}/5"


class ValoracionServicio(ModeloBase):
    """Modelo para valoraciones de servicios de reparación."""
    
    servicio = models.ForeignKey(
        'reparaciones.ServicioReparacion',
        verbose_name=_('servicio'),
        on_delete=models.CASCADE,
        related_name='valoraciones'
    )
    cliente = models.ForeignKey(
        Cliente,
        verbose_name=_('cliente'),
        on_delete=models.CASCADE,
        related_name='valoraciones_servicio'
    )
    reparacion = models.ForeignKey(
        'reparaciones.Reparacion',
        verbose_name=_('reparación'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='valoraciones'
    )
    puntuacion = models.PositiveSmallIntegerField(
        _('puntuación'),
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    titulo = models.CharField(_('título'), max_length=100)
    comentario = models.TextField(_('comentario'))
    fecha = models.DateTimeField(_('fecha'), auto_now_add=True)
    aprobado = models.BooleanField(_('aprobado'), default=False)
    
    class Meta:
        verbose_name = _('valoración de servicio')
        verbose_name_plural = _('valoraciones de servicios')
        ordering = ['-fecha']
        unique_together = ('servicio', 'cliente', 'reparacion')
    
    def __str__(self):
        return f"{self.cliente} - {self.servicio} - {self.puntuacion}/5"