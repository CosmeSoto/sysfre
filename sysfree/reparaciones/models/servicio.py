from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from core.models import ModeloBase
from inventario.models import Producto
from reparaciones.models.reparacion import Reparacion


class ServicioReparacion(ModeloBase):
    """Modelo para servicios de reparación que se pueden ofrecer en la tienda."""
    
    TIPO_CHOICES = (
        ('diagnostico', _('Diagnóstico')),
        ('reparacion', _('Reparación')),
        ('mantenimiento', _('Mantenimiento')),
        ('instalacion', _('Instalación')),
        ('configuracion', _('Configuración')),
        ('otro', _('Otro')),
    )
    
    nombre = models.CharField(_('nombre'), max_length=200)
    descripcion = models.TextField(_('descripción'))
    tipo = models.CharField(_('tipo'), max_length=15, choices=TIPO_CHOICES, default='reparacion')
    precio = models.DecimalField(_('precio'), max_digits=10, decimal_places=2)
    tiempo_estimado = models.PositiveIntegerField(_('tiempo estimado (horas)'), default=1)
    producto = models.OneToOneField(
        Producto,
        verbose_name=_('producto asociado'),
        on_delete=models.CASCADE,
        related_name='servicio_reparacion',
        null=True,
        blank=True
    )
    reparaciones = models.ManyToManyField(
        Reparacion,
        verbose_name=_('reparaciones'),
        related_name='servicios',
        blank=True
    )
    requiere_diagnostico_previo = models.BooleanField(_('requiere diagnóstico previo'), default=False)
    disponible_online = models.BooleanField(_('disponible online'), default=True)
    
    class Meta:
        verbose_name = _('servicio de reparación')
        verbose_name_plural = _('servicios de reparación')
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre
    
    def clean(self):
        """Valida que el precio no sea negativo y sincroniza con producto."""
        if self.precio < 0:
            raise ValidationError(_('El precio no puede ser negativo.'))
        # Asegura que el producto esté configurado como servicio y no inventariable
        if self.producto:
            if getattr(self.producto, 'tipo', None) != 'servicio':
                raise ValidationError(_('El producto asociado debe ser de tipo "servicio".'))
            if getattr(self.producto, 'es_inventariable', True):
                raise ValidationError(_('El producto asociado no debe ser inventariable.'))
            # Sincroniza el precio
            if self.producto.precio != self.precio:
                self.producto.precio = self.precio
                self.producto.save()
        super().clean()